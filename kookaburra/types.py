from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Json, StrictInt, StrictStr, validator


class BaseResponse(BaseModel):
    message: StrictStr


class HealthResponse(BaseResponse):
    message: StrictStr
    version: StrictStr
    time: datetime


class Scope(BaseModel):
    type: StrictStr
    asgi: Optional[Dict]
    http_version: StrictStr
    method: StrictStr
    scheme: StrictStr
    root_path: Optional[StrictStr]
    path: StrictStr
    raw_path: Optional[str]
    headers: List
    query_string: bytes


class RequestLoggerMessage(BaseModel):
    scope: Scope
    _stream_consumed: bool
    _is_disconnected: bool


class ResponseLoggerMessage(BaseModel):
    status_code: StrictInt
    raw_headers: List


class JsonResponseLoggerMessage(BaseModel):
    body: Json


class GitHubToken(BaseModel):
    access_token: StrictStr
    token_type: StrictStr
    scope: StrictStr


class LoginGitHubResponse(BaseModel):
    url: StrictStr


class GitHubUserData(BaseModel):
    emails: List
    raw_data: Dict
    waitlisted: bool = True

    @validator("emails")
    def filter_emails(cls, emails: List) -> List:
        return [
            EmailStr(dict(e)["email"]) for e in emails if cls._gh_email_filter(dict(e))
        ]

    @staticmethod
    def _gh_email_filter(email: Dict) -> bool:
        return email["verified"] and (
            not email["email"].endswith("users.noreply.github.com")
        )

    @property
    def is_authenticated(self) -> bool:
        return len(self.emails) > 0

    @property
    def display_name(self) -> EmailStr:
        return self.raw_data["login"]


class SMSResponse(BaseResponse):
    ...


class UploadContentResponse(BaseResponse):
    ...
