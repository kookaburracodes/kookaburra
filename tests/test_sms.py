import urllib.parse
from unittest import mock

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.const import API_V0
from kookaburra.models import GitHubUser, GitHubUserCreate, Llm, LLMCreate
from kookaburra.types import BaseResponse
from tests.mocks import MockGoogleCloudStorageClient


async def test_sms_no_llm(server: AsyncClient) -> None:
    data = "&".join(
        [
            "To=" + urllib.parse.quote("+15555555555"),
            "From=" + urllib.parse.quote("+15555555554"),
            "Body=" + urllib.parse.quote("Hello world"),
        ]
    )
    response = await server.post(f"{API_V0}/sms", data=data)  # type: ignore
    assert response.status_code == 200


@mock.patch(
    "kookaburra.api.twilio_svc.send_message",
    return_value=None,
)
@mock.patch(
    "kookaburra.api.llm_svc.respond",
    return_value=BaseResponse(message="hello world!"),
)
@mock.patch(
    "kookaburra.gs.GsService._gs",
    return_value=MockGoogleCloudStorageClient,
)
async def test_sms_llm(
    mock_google_storage: mock.MagicMock,
    mock_llm_respond: mock.MagicMock,
    mock_twilio: mock.MagicMock,
    server: AsyncClient,
    async_db_session: AsyncSession,
) -> None:
    async with async_db_session.begin():
        ghuser_create = GitHubUserCreate(
            username="user",
            emails=["user@example.com"],
        )
        user = GitHubUser(**ghuser_create.dict())
        async_db_session.add(user)
        await async_db_session.commit()
        assert user.id is not None

    async with async_db_session.begin():
        llm_Create = LLMCreate(
            phone_number="+15555555555",
            modal_url="https://example.com",
            clone_url="https://github.com",
            githubuser_id=user.id,
        )
        llm = Llm(**llm_Create.dict())
        async_db_session.add(llm)
        await async_db_session.commit()
        assert llm.id is not None

    data = "&".join(
        [
            "To=" + urllib.parse.quote("+15555555555"),
            "From=" + urllib.parse.quote("+15555555554"),
            "Body=" + urllib.parse.quote("Hello world"),
        ]
    )
    response = await server.post(f"{API_V0}/sms", data=data)  # type: ignore
    assert response.status_code == 200
