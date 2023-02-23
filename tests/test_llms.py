import base64
import json
import time
from unittest import mock
from uuid import uuid4

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.const import API_V0
from kookaburra.llm import llm_svc
from kookaburra.models import GitHubUser, GitHubUserCreate, Llm, LLMCreate
from kookaburra.types import GitHubUserAuthToken
from kookaburra.utils import _encrypt


async def test_get_llm_no_user(server: AsyncClient) -> None:
    response = await server.delete(f"{API_V0}/llm/{uuid4()}")  # type: ignore
    assert response.status_code == 403
    assert response.json() == {"detail": "Please sign up!"}


@mock.patch(
    "kookaburra.llm.twilio_svc.release_phone_number",
    return_value=None,
)
async def test_delete_llm(
    mock_release_phone_number: mock.MagicMock,
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

    response = await server.delete(
        f"{API_V0}/llm/{llm.id}", cookies={"kb_auth_token": kb_auth_token}
    )
    assert response.status_code == 200


@mock.patch(
    "kookaburra.llm.twilio_svc.release_phone_number",
    return_value=None,
)
async def test_delete_llm_no_current_user(
    mock_release_phone_number: mock.MagicMock,
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

    kb_auth_token = _encrypt(
        base64.b64encode(
            json.dumps(
                GitHubUserAuthToken(
                    display_name="user",
                    emails=["user@example.com"],
                    raw_data={"login": "user"},
                    expiry=time.time() - 30,
                ).dict()
            ).encode("utf8")
        )
    ).decode()

    response = await server.delete(
        f"{API_V0}/llm/{llm.id}", cookies={"kb_auth_token": kb_auth_token}
    )
    assert response.status_code == 403


async def test_delete_llm_no_llm(
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

    response = await server.delete(
        f"{API_V0}/llm/{uuid4()}",
        cookies={"kb_auth_token": kb_auth_token},
    )
    assert response.status_code == 400


async def test_create_llm(
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

    llm = await llm_svc.create(
        clone_url="https://github.com",
        psql=async_db_session,
        user=user,
        phone_number="+15555555555",
    )

    assert llm is not None
    assert llm.id is not None
    assert llm.phone_number == "+15555555555"
    assert llm.modal_url == f"https://kookaburracodes--{llm.id}--api.modal.run/"
    assert llm.clone_url == "https://github.com"

    _llm = await llm_svc.get_by_clone_url(
        clone_url="https://github.com", psql=async_db_session
    )
    assert _llm == llm
