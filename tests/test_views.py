import base64
import json
import time

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.models import GitHubUser, GitHubUserCreate
from kookaburra.types import GitHubUserAuthToken
from kookaburra.utils import _encrypt


async def test_home_page(server: AsyncClient) -> None:
    response = await server.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


async def test_home_page_with_user(
    server: AsyncClient, async_db_session: AsyncSession
) -> None:
    async with async_db_session.begin():
        ghusercreate = GitHubUserCreate(
            username="user",
            emails=["user@example.com"],
        )
        user = GitHubUser(**ghusercreate.dict())
        async_db_session.add(user)
        await async_db_session.commit()
        assert user.id is not None

    kb_auth_token = _encrypt(
        base64.b64encode(
            json.dumps(
                GitHubUserAuthToken(
                    display_name="user",
                    emails=["user@example.com"],
                    raw_data={"login": "user"},
                    expiry=time.time() + 30,
                ).dict()
            ).encode("utf8")
        )
    ).decode()

    response = await server.get("/", cookies={"kb_auth_token": kb_auth_token})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


async def test_missing_page(server: AsyncClient) -> None:
    response = await server.get("/not-found")
    assert response.status_code == 307
    assert response.headers["location"] == "/404"
    response = await server.get("/404")
    assert response.status_code == 200
