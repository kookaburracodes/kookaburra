import os

from httpx import AsyncClient

from kookaburra import __version__
from kookaburra.const import API_V0


async def test_tz() -> None:
    assert os.environ["TZ"] == "UTC"


async def test_healthcheck(server: AsyncClient) -> None:
    response = await server.get(f"{API_V0}/healthcheck")
    assert response.status_code == 200
    assert response.json()["message"] == "🪶"
    assert response.json()["version"] == __version__
