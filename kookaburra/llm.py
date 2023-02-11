from typing import Optional
from uuid import uuid4

import httpx
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.deployment import deploy_svc
from kookaburra.models import Llm, User
from kookaburra.types import BaseResponse


class LlmService:
    async def get_by_clone_url(
        self, clone_url: str, psql: AsyncSession
    ) -> Optional[Llm]:
        results = (
            (
                await psql.execute(
                    select(Llm).where(
                        Llm.clone_url == clone_url,
                    )
                )
            )
            .scalars()
            .first()
        )
        return results

    async def create_llm(
        self, clone_url: str, psql: AsyncSession, user: User, phone_number: str
    ) -> Llm:
        llm_id = uuid4()
        modal_url = deploy_svc.get_modal_url(llm_id=str(llm_id))
        llm = Llm(
            id=llm_id,
            clone_url=clone_url,
            phone_number=phone_number,
            modal_url=modal_url,
            user_id=user.id,
        )
        psql.add(llm)
        await psql.commit()
        await psql.refresh(llm)
        return llm

    async def get_llm_by_phone_number(
        self, phone_number: str, psql: AsyncSession
    ) -> Optional[Llm]:
        results = (
            (await psql.execute(select(Llm).where(Llm.phone_number == phone_number)))
            .scalars()
            .first()
        )
        return results

    async def respond(
        self,
        llm: Llm,
        message: str,
    ) -> BaseResponse:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{llm.modal_url.strip('/')}/hey",
                json={
                    "message": message,
                },
            )
            return BaseResponse(**response.json())


llm_svc = LlmService()
