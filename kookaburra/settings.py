import os
import sys

from pydantic import BaseSettings, Field


class _Env(BaseSettings):
    #
    #   Required
    #
    API_SECRET_KEY: str = Field(
        ...,
        env="API_SECRET_KEY",
        description="The API secret key.",
    )
    API_SALT: str = Field(
        ...,
        env="API_SALT",
        description="The API salt.",
    )
    KOOKABURRA_URL: str = Field(
        ...,
        env="KOOKABURRA_URL",
        description="The root url (/).",
    )
    OPENAI_API_KEY: str = Field(
        ...,
        env="OPENAI_API_KEY",
        description="The OpenAI API key.",
    )
    TWILIO_ACCOUNT_SID: str = Field(
        ...,
        env="TWILIO_ACCOUNT_SID",
        description="The kookaburra twilio account sid",
    )
    TWILIO_AUTH_TOKEN: str = Field(
        ...,
        env="TWILIO_AUTH_TOKEN",
        description="The kookaburra twilio auth token",
    )
    #
    #   Optional
    #
    MODAL_TOKEN_ID: str = Field(
        "",
        env="MODAL_TOKEN_ID",
        description="The modal token id.",
    )
    MODAL_TOKEN_SECRET: str = Field(
        "",
        env="MODAL_TOKEN_SECRET",
        description="The modal token secret.",
    )
    LOG_LEVEL: str = Field(
        "WARNING",
        env="LOG_LEVEL",
        description="Log level.",
    )
    GH_APP_ID: str = Field(
        "",
        env="GH_APP_ID",
        description="The GitHub App ID.",
    )
    GH_APP_PRIVATE_KEY_PATH: str = Field(
        "",
        env="GH_APP_PRIVATE_KEY_PATH",
        description="The GitHub App private key path.",
    )
    GH_CLIENT_ID: str = Field(
        "",
        env="GH_CLIENT_ID",
        description="The GitHub OAuth client ID.",
    )
    GH_CLIENT_SECRET: str = Field(
        "",
        env="GH_CLIENT_SECRET",
        description="The GitHub OAuth client secret.",
    )
    GH_OAUTH_SCOPE: str = Field(
        "read:user,user:email",
        env="GH_OAUTH_SCOPE",
        description="The GitHub OAuth scope.",
    )
    GH_OAUTH_ENDPOINT: str = Field(
        "https://github.com/login/oauth/authorize",
        env="GH_OAUTH_ENDPOINT",
        description="The GitHub OAuth endpoint.",
    )
    GH_TOKEN_ENDPOINT: str = Field(
        "https://github.com/login/oauth/access_token",
        env="GH_TOKEN_ENDPOINT",
        description="The GitHub OAuth token endpoint.",
    )
    PSQL_URL: str = Field(
        "postgresql+asyncpg://kookaburra:kookaburra@localhost:5432/kookaburra",
        env="PSQL_URL",
        description="The PSQL database URL.",
    )
    PSQL_POOL_SIZE: int = Field(
        5,
        env="PSQL_POOL_SIZE",
        description="The PSQL database pool size.",
    )
    PSQL_MAX_OVERFLOW: int = Field(
        10,
        env="PSQL_MAX_OVERFLOW",
        description="The PSQL database max overflow.",
    )
    PSQL_POOL_PRE_PING: bool = Field(
        True,
        env="PSQL_POOL_PRE_PING",
        description="The PSQL database pre pool ping.",
    )

    class Config:
        env_file = ".env.local"
        env_encoding = "utf-8"


if os.getenv("_", "").endswith("pytest") or "pytest" in "".join(sys.argv):
    _Env.Config.env_file = ".env.test"  # type: ignore

env = _Env()

# if the ENV_FILE environment variable is set, use it as an override
# this is useful for running alembic migrations against remote databases
if os.getenv("ENV_FILE") is not None:
    env = _Env(_env_file=os.environ["ENV_FILE"])  # pragma: no cover
