from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, EmailStr
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


class TimestampsMixin(BaseModel):
    created_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            default=datetime.utcnow,
            nullable=False,
        )
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        )
    )


class UUIDMixin(BaseModel):
    id: UUID4 = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class BaseUser(SQLModel):
    email: EmailStr = Field(
        index=True,
        unique=True,
        nullable=False,
    )

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
            }
        }


class UserCreate(BaseUser):
    ...


class User(
    BaseUser,
    UUIDMixin,
    TimestampsMixin,
    table=True,
):
    __tablename__ = "users"
    llms: List["Llm"] = Relationship(
        sa_relationship_kwargs=dict(
            back_populates="user",
            cascade="all,delete,delete-orphan",
            order_by="Llm.created_at.desc()",
        ),
    )


class UserRead(
    BaseUser,
    UUIDMixin,
    TimestampsMixin,
):
    llms: List["Llm"]


class BaseLlm(SQLModel):
    phone_number: str = Field(
        index=True,
        unique=True,
        nullable=False,
    )
    modal_url: str = Field(
        unique=True,
        nullable=False,
    )
    clone_url: str = Field(
        unique=True,
        nullable=False,
    )

    class Config:
        schema_extra = {
            "example": {
                "modal_url": "https://kookaburracodes--kb-test--api.modal.run/",
                "phone_number": "+15555555555",
                "clone_url": "https://github.com/kookaburracodes/"
                "kookaburra-simple-example.git",
            }
        }


class LLMCreate(BaseLlm):
    user_id: UUID4


class Llm(
    BaseLlm,
    UUIDMixin,
    TimestampsMixin,
    table=True,
):
    __tablename__ = "llms"

    user_id: UUID4 = Field(
        default=None,
        foreign_key="users.id",
        nullable=False,
    )
    user: User = Relationship(
        back_populates="llms",
    )


UserRead.update_forward_refs()
