import base64
import urllib.parse
from datetime import datetime

from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra import __version__
from kookaburra.const import (
    API_V0,
    KB_AUTH_TOKEN,
    KB_AUTH_TOKEN_EXPIRE_SECONDS,
    LOCAL_DOMAINS,
)
from kookaburra.db import psql_db
from kookaburra.gh import gh_svc
from kookaburra.llm import llm_svc
from kookaburra.log import log
from kookaburra.models import GitHubUserCreate
from kookaburra.settings import env
from kookaburra.twilio import twilio_svc
from kookaburra.types import (
    BaseResponse,
    GitHubToken,
    GitHubUserAuthToken,
    HealthResponse,
    SMSResponse,
)
from kookaburra.user import githubuser_svc
from kookaburra.utils import _APIRoute, _encrypt

health_router = APIRouter(
    route_class=_APIRoute,
    tags=["health"],
    prefix=API_V0,
)
sms_router = APIRouter(
    route_class=_APIRoute,
    tags=["sms"],
    prefix=API_V0,
)
gh_router = APIRouter(
    route_class=_APIRoute,
    tags=["gh"],
    prefix=API_V0,
)
llm_router = APIRouter(
    route_class=_APIRoute,
    tags=["llm"],
    prefix=API_V0,
)


@health_router.get(
    "/healthcheck",
    response_model=HealthResponse,
)
async def get_health() -> HealthResponse:
    """Get the health of the server.
    Returns:
        HealthResponse: The health of the server.
    """
    log.info("Healthcheck!")
    return HealthResponse(
        message="🪶",
        version=__version__,
        time=datetime.utcnow(),
    )


@sms_router.post(
    "/sms",
    response_model=SMSResponse,
)
async def send_message(
    request: Request,
    psql: AsyncSession = Depends(psql_db),
) -> SMSResponse:
    """Send a message.
    Args:
        message (MessageRequest): The message to send.
    Returns:
        MessageResponse: The response from the message.
    """
    _body = await request.body()
    body = {
        v.split("=")[0]: v.split("=")[1]
        for v in urllib.parse.unquote_plus(_body.decode("utf8")).split("&")
    }
    llm = await llm_svc.get_llm_by_phone_number(
        phone_number=body["To"],
        psql=psql,
    )
    if not llm:
        log.error(f"Could not find LLM for phone number {body['To']}")
        return SMSResponse(message="🪶")
    response = await llm_svc.respond(
        llm=llm,
        message=body["Body"],
    )
    twilio_svc.send_message(
        from_number=body["To"],
        to_number=body["From"],
        message=response.message,
    )
    return SMSResponse(message="🪶")


@gh_router.get(
    "/login/gh",
    response_class=Response,
)
async def login_gh(request: Request) -> Response:
    redirect_uri = request.url_for("auth_github")
    if not any(
        [n in env.KOOKABURRA_URL for n in LOCAL_DOMAINS],
    ):
        redirect_uri = redirect_uri.replace(
            "http://",
            "https://",
        )
    client = AsyncOAuth2Client(
        redirect_uri=redirect_uri,
        client_id=env.GH_CLIENT_ID,
        client_secret=env.GH_CLIENT_SECRET,
        scope=env.GH_OAUTH_SCOPE,
    )
    uri, state = client.create_authorization_url(
        env.GH_OAUTH_ENDPOINT,
    )
    return Response(
        status_code=200,
        headers={"HX-Redirect": uri},
    )


@gh_router.get(
    "/auth/gh",
    response_class=RedirectResponse,
)
async def auth_github(
    request: Request,
    psql: AsyncSession = Depends(psql_db),
) -> RedirectResponse:
    """Redirect to GitHub OAuth."""
    client = AsyncOAuth2Client(
        client_id=env.GH_CLIENT_ID,
        client_secret=env.GH_CLIENT_SECRET,
        scope=env.GH_OAUTH_SCOPE,
    )
    fetch_token_res = await client.fetch_token(
        url=env.GH_TOKEN_ENDPOINT,
        authorization_response=str(request.url),
    )
    token = GitHubToken(**fetch_token_res)
    gh_user = await gh_svc.get_gh_user_data(
        token=token,
    )
    user = await githubuser_svc.get_by_name(
        psql=psql,
        username=gh_user.raw_data["login"],
    )
    if not user:
        user = await githubuser_svc.create(
            psql=psql,
            user_create=GitHubUserCreate(
                username=gh_user.raw_data["login"],
                emails=gh_user.emails,
            ),
        )
    expiry = int((datetime.utcnow() + KB_AUTH_TOKEN_EXPIRE_SECONDS).strftime("%s"))
    cookie_value = (
        GitHubUserAuthToken(
            display_name=gh_user.raw_data["login"],
            expiry=expiry,
            emails=gh_user.emails,
            raw_data=gh_user.raw_data,
        )
        .json()
        .encode("utf8")
    )
    encoded_cookie_value = base64.b64encode(cookie_value)
    response = RedirectResponse(
        url=f"{env.KOOKABURRA_URL}/?success=true",
    )
    response.set_cookie(
        key=KB_AUTH_TOKEN,
        value=_encrypt(encoded_cookie_value).decode("utf8"),
        expires=expiry,
        httponly=True,
    )
    return response


@gh_router.post(
    "/wh/gh",
    response_class=Response,
)
async def wh_github(
    request: Request,
    psql: AsyncSession = Depends(psql_db),
) -> Response:
    """Handle GitHub webhook."""
    headers = request.headers
    request = await request.json()
    user = await githubuser_svc.get_by_name(
        username=request["pusher"]["name"],
        psql=psql,
    )
    if user is None:
        raise HTTPException(
            status_code=403,
            detail="Please sign up!",
        )
    if user.waitlisted:
        raise HTTPException(
            status_code=403,
            detail="You are waitlisted!",
        )
    await gh_svc.handle_webhook(  # pragma: no cover
        request=dict(request),
        headers=dict(headers),
        psql=psql,
        user=user,
    )
    return Response(status_code=200)  # pragma: no cover


@llm_router.delete(
    "/llm/{llm_id}",
    response_model=BaseResponse,
)
async def delete(
    llm_id: UUID4,
    request: Request,
    psql: AsyncSession = Depends(psql_db),
) -> BaseResponse:
    current_githubuser = await githubuser_svc.get_current_user(
        request=request,
        psql=psql,
    )
    if not current_githubuser:
        raise HTTPException(
            status_code=403,
            detail="Please sign up!",
        )
    await llm_svc.delete(
        llm_id=llm_id,
        githubuser_id=current_githubuser.id,
        psql=psql,
    )
    return BaseResponse(message="🪶")
