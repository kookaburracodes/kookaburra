from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, EmailStr
from sqlalchemy import Column, DateTime
from sqlmodel import JSON, Field, Relationship, SQLModel


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


class BaseGitHubUser(SQLModel):
    username: str = Field(
        index=True,
        unique=True,
        nullable=False,
    )
    emails: List[EmailStr] = Field(
        sa_column=Column(JSON),
        index=False,
        nullable=False,
    )
    waitlisted: bool = Field(
        default=True,
        index=False,
        nullable=False,
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "username",
                "emails": ["user@example.com"],
            }
        }


class GitHubUserCreate(BaseGitHubUser):
    ...


class GitHubUser(
    BaseGitHubUser,
    UUIDMixin,
    TimestampsMixin,
    table=True,
):
    __tablename__ = "githubusers"
    llms: List["Llm"] = Relationship(
        sa_relationship_kwargs=dict(
            back_populates="githubuser",
            cascade="all,delete,delete-orphan",
            order_by="Llm.created_at.desc()",
        ),
    )


class GitHubUserRead(
    BaseGitHubUser,
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
    githubuser_id: UUID4


class Llm(
    BaseLlm,
    UUIDMixin,
    TimestampsMixin,
    table=True,
):
    __tablename__ = "llms"

    githubuser_id: UUID4 = Field(
        default=None,
        foreign_key="githubusers.id",
        nullable=False,
    )
    githubuser: GitHubUser = Relationship(
        back_populates="llms",
    )


GitHubUser.update_forward_refs()
