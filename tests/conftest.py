import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import Request
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.db import async_psql_engine
from kookaburra.main import app as server_app


@pytest_asyncio.fixture(
    scope="session",
)
async def server() -> AsyncGenerator:
    async with AsyncClient(
        app=server_app,
        base_url="http://testserver:8001",
    ) as server:
        yield server


@pytest_asyncio.fixture(
    scope="function",
    autouse=True,
)
async def async_db_session() -> AsyncGenerator:
    session = sessionmaker(
        async_psql_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session() as s:
        async with async_psql_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        yield s

    async with async_psql_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_psql_engine.dispose()


@pytest.fixture(
    scope="session",
    autouse=True,
)
def event_loop(request: Request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
