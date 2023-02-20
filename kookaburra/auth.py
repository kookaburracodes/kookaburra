import base64
import json
from typing import Optional, Tuple

from cryptography.fernet import InvalidToken
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)
from starlette.requests import HTTPConnection

from kookaburra.gh import gh_svc
from kookaburra.log import log
from kookaburra.types import GitHubToken, GitHubUserData
from kookaburra.utils import _decrypt


class GitHubAuthBackend(AuthenticationBackend):
    async def authenticate(  # type: ignore
        self, request: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, GitHubUserData]]:
        log.debug("GitHubAuthBackend.authenticate")
        gh_token = request.cookies.get("gh_token")
        if gh_token:
            try:
                _decrypted_decoded_gh_token = base64.b64decode(
                    _decrypt(gh_token).decode("utf8")
                )
            except InvalidToken:
                request.cookies.pop("gh_token")
                return None
            try:
                user = await gh_svc.get_gh_user_data(
                    token=GitHubToken(**json.loads(_decrypted_decoded_gh_token))
                )
                return AuthCredentials(["authenticated"]), user
            except Exception:
                raise AuthenticationError()
        return None
