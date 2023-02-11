from datetime import datetime

from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra import __version__
from kookaburra.const import API_V0, LOCAL_DOMAINS
from kookaburra.db import psql_db
from kookaburra.gh import gh_svc
from kookaburra.log import log
from kookaburra.settings import env
from kookaburra.twilio import twilio_svc
from kookaburra.types import GitHubToken, HealthResponse, SMSResponse
from kookaburra.user import user_svc
from kookaburra.utils import _APIRoute

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
    await twilio_svc.respond(request=request, psql=psql)
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
) -> RedirectResponse:  # pragma: no cover
    """Redirect to GitHub OAuth."""
    client = AsyncOAuth2Client(
        client_id=env.GH_CLIENT_ID,
        client_secret=env.GH_CLIENT_SECRET,
        scope=env.GH_OAUTH_SCOPE,
    )
    token = await client.fetch_token(
        url=env.GH_TOKEN_ENDPOINT,
        authorization_response=str(request.url),
    )
    gh_user = await gh_svc.get_user(
        token=GitHubToken(**token),
    )
    await user_svc.create_from_list_of_emails(
        emails=gh_user.emails,
        psql=psql,
    )
    return RedirectResponse(
        url=f"{env.KOOKABURRA_URL}/?success=true",
    )


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
    if request is not None:
        user = await user_svc.get_by_email(
            email=request["pusher"]["email"],
            psql=psql,
        )
        if user is None:
            raise HTTPException(
                status_code=403,
                detail="Please sign up!",
            )
        await gh_svc.handle_webhook(
            request=dict(request),
            headers=dict(headers),
            psql=psql,
            user=user,
        )
    return Response(status_code=200)
