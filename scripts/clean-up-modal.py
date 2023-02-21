import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sh
from google.protobuf import empty_pb2  # type: ignore
from modal.client import AioClient
from modal_proto import api_pb2
from modal_utils.async_utils import synchronizer
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.db import async_psql_engine
from kookaburra.models import Llm


@asynccontextmanager
async def psql_db() -> AsyncGenerator:
    async_session = sessionmaker(
        async_psql_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@synchronizer
async def delete_old_apps(llm_ids: list[str]) -> None:
    """List all running or recently running Modal apps for the current account"""
    aio_client = await AioClient.from_env()
    res: api_pb2.AppListResponse = await aio_client.stub.AppList(empty_pb2.Empty())
    for app_stats in res.apps:
        app_id = app_stats.app_id
        desc = app_stats.description
        print(app_id, desc)
        if desc in llm_ids:
            if desc not in llm_ids:
                print("stopping", app_id)
                sh.modal(
                    "app",
                    "stop",
                    app_id,
                )


async def get_llm_ids() -> list[str]:
    async with psql_db() as session:
        llms = await session.execute(select(Llm))
        llm_ids = [str(llm.id) for llm in llms.scalars().all()]
    return llm_ids


async def main() -> None:
    llm_ids = await get_llm_ids()
    await delete_old_apps(llm_ids=llm_ids)


if __name__ == "__main__":
    asyncio.run(main())
