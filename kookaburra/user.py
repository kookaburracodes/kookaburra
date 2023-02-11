from typing import List, Optional

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.models import User, UserCreate


class UserService:
    async def get_by_email(
        self,
        email: str,
        psql: AsyncSession,
    ) -> Optional[User]:
        results = await psql.execute(
            select(User).where(User.email == email),
        )
        return results.scalars().first()

    async def create(
        self,
        user_create: UserCreate,
        psql: AsyncSession,
    ) -> User:
        user = User(email=user_create.email)
        psql.add(user)
        await psql.commit()
        await psql.refresh(user)
        return user

    async def list(
        self,
        psql: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        results = await psql.execute(
            select(User).offset(skip).limit(limit).order_by(desc(User.created_at))
        )
        return results.scalars().all()

    async def create_from_list_of_emails(
        self, emails: List, psql: AsyncSession
    ) -> None:
        for email in emails:
            user = await self.get_by_email(
                psql=psql,
                email=email,
            )
            if not user:
                await self.create(
                    psql=psql,
                    user_create=UserCreate(
                        email=email,
                    ),
                )


user_svc = UserService()
