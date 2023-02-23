from unittest import mock

from httpx import AsyncClient

from kookaburra.const import API_V0
from kookaburra.settings import env
from tests.mocks import MockAsyncOAuth2Client, MockGithub


async def test_login_gh(
    server: AsyncClient,
) -> None:
    response = await server.get(f"{API_V0}/login/gh")  # type: ignore
    assert response.status_code == 200
    assert response.headers["HX-Redirect"].startswith("https://github.com")


@mock.patch(
    "kookaburra.api.AsyncOAuth2Client",
    return_value=MockAsyncOAuth2Client,
)
@mock.patch(
    "kookaburra.gh.Github",
    return_value=MockGithub,
)
async def test_auth_github(
    mock_github: mock.MagicMock,
    mock_async_oauth2_client: mock.MagicMock,
    server: AsyncClient,
) -> None:
    response = await server.get(f"{API_V0}/auth/gh")  # type: ignore
    assert response.status_code == 307
    assert response.headers["location"].startswith(
        env.KOOKABURRA_URL,
    )
