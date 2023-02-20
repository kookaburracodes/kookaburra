from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.db import psql_db
from kookaburra.llm import llm_svc
from kookaburra.user import githubuser_svc
from kookaburra.utils import _APIRoute

templates = Jinja2Templates(
    directory="templates",
)

views = APIRouter(
    route_class=_APIRoute,
    tags=["views"],
)


@views.get(
    "/",
    response_class=HTMLResponse,
)
async def _index(
    request: Request,
    psql: AsyncSession = Depends(psql_db),
) -> Response:
    llms = []
    if request.user.is_authenticated:
        user = await githubuser_svc.get_by_name(
            username=request.user.raw_data["login"],
            psql=psql,
        )
        if user:
            request.user.waitlisted = user.waitlisted
            llms = await llm_svc.get_llms_for_user(
                user=user,
                psql=psql,
            )
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "llms": llms,
        },
    )


@views.get(
    "/404",
    response_class=HTMLResponse,
)
async def _not_found(request: Request) -> Response:
    return templates.TemplateResponse(
        name="404.html",
        context={"request": request},
    )
