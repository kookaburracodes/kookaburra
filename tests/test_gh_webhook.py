from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.const import API_V0
from kookaburra.models import GitHubUser, GitHubUserCreate


async def test_gh_webhook_waitlisted_user(
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

    payload = {"pusher": {"name": "user"}}
    res = await server.post(
        f"{API_V0}/wh/gh",
        json=payload,
    )
    assert res.status_code == 403
    assert res.json() == {
        "detail": "You are waitlisted!",
    }


async def test_gh_webhook_no_user(server: AsyncClient) -> None:
    payload = {"pusher": {"name": "user"}}
    res = await server.post(
        f"{API_V0}/wh/gh",
        json=payload,
    )
    assert res.status_code == 403
    assert res.json() == {
        "detail": "Please sign up!",
    }
