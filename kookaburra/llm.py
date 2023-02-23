from typing import List, Optional
from uuid import uuid4

import httpx
from fastapi import HTTPException, status
from pydantic import UUID4
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.deployment import deploy_svc
from kookaburra.models import GitHubUser, Llm
from kookaburra.twilio import twilio_svc
from kookaburra.types import BaseResponse


class LlmService:
    async def get_by_clone_url(
        self,
        clone_url: str,
        psql: AsyncSession,
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

    async def create(
        self,
        clone_url: str,
        psql: AsyncSession,
        user: GitHubUser,
        phone_number: str,
    ) -> Llm:
        llm_id = uuid4()
        modal_url = deploy_svc.get_modal_url(llm_id=str(llm_id))
        llm = Llm(
            id=llm_id,
            clone_url=clone_url,
            phone_number=phone_number,
            modal_url=modal_url,
            githubuser_id=user.id,
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
    ) -> BaseResponse:  # pragma: no cover
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{llm.modal_url.strip('/')}/hey",
                json={
                    "message": message,
                },
            )
            return BaseResponse(**response.json())

    async def get_llms_for_user(
        self,
        user: GitHubUser,
        psql: AsyncSession,
    ) -> List[Llm]:
        results = (
            (await psql.execute(select(Llm).where(Llm.githubuser_id == user.id)))
            .scalars()
            .all()
        )
        return results

    async def get_for_user(
        self,
        llm_id: UUID4,
        githubuser_id: UUID4,
        psql: AsyncSession,
    ) -> Optional[Llm]:
        results = (
            (
                await psql.execute(
                    select(Llm)
                    .where(Llm.id == llm_id)
                    .where(Llm.githubuser_id == githubuser_id)
                )
            )
            .scalars()
            .first()
        )
        return results

    async def delete(
        self,
        llm_id: UUID4,
        githubuser_id: UUID4,
        psql: AsyncSession,
    ) -> None:
        llm = await self.get_for_user(
            llm_id=llm_id,
            githubuser_id=githubuser_id,
            psql=psql,
        )
        if llm is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bad request.",
            )
        await psql.delete(llm)
        await psql.commit()
        phone_number = llm.phone_number
        await twilio_svc.release_phone_number(phone_number)
        # TODO: stop the deployed modal app
        # _llm_id = str(llm.id)
        # await deploy_svc.stop_modal_app(_llm_id)
        # for now this script is run manually
        # scripts/clean-up-modal.py


llm_svc = LlmService()
