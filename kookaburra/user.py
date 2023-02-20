from typing import Optional

from fastapi import Request
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.models import GitHubUser, GitHubUserCreate


class GitHubUserService:
    async def get(self, psql: AsyncSession, githubuser_id: str) -> Optional[GitHubUser]:
        results = await psql.execute(
            select(GitHubUser).where(GitHubUser.id == githubuser_id),
        )
        return results.scalars().first()

    async def get_by_name(
        self,
        username: str,
        psql: AsyncSession,
    ) -> Optional[GitHubUser]:
        results = await psql.execute(
            select(GitHubUser).where(GitHubUser.username == username),
        )
        return results.scalars().first()

    async def create(
        self,
        user_create: GitHubUserCreate,
        psql: AsyncSession,
    ) -> GitHubUser:
        user = GitHubUser(**user_create.dict())
        psql.add(user)
        await psql.commit()
        await psql.refresh(user)
        return user

    async def list(
        self,
        psql: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[GitHubUser]:
        results = await psql.execute(
            select(GitHubUser)
            .offset(skip)
            .limit(limit)
            .order_by(desc(GitHubUser.created_at))
        )
        return results.scalars().all()

    async def get_current_user(
        self,
        request: Request,
        psql: AsyncSession,
    ) -> Optional[GitHubUser]:
        if not request.user.is_authenticated:
            return None
        return await self.get_by_name(
            username=request.user.raw_data["login"],
            psql=psql,
        )


githubuser_svc = GitHubUserService()
