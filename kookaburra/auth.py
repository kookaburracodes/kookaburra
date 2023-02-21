import base64
import json
from typing import Optional, Tuple

from cryptography.fernet import InvalidToken
from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.requests import HTTPConnection

from kookaburra.const import KB_AUTH_TOKEN
from kookaburra.log import log
from kookaburra.types import GitHubUserAuthToken
from kookaburra.utils import _decrypt


class GitHubAuthBackend(AuthenticationBackend):
    async def authenticate(  # type: ignore
        self, request: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, GitHubUserAuthToken]]:
        log.debug("GitHubAuthBackend.authenticate")
        kb_auth_token = request.cookies.get(KB_AUTH_TOKEN)
        if kb_auth_token is not None:
            try:
                _decrypted_decoded_gh_token = base64.b64decode(
                    _decrypt(kb_auth_token).decode("utf8")
                )
            except InvalidToken:
                request.cookies.pop(KB_AUTH_TOKEN)
                return None
            try:
                token = GitHubUserAuthToken(**json.loads(_decrypted_decoded_gh_token))
                assert not token.expired
                return AuthCredentials(["authenticated"]), token
            except Exception:
                request.cookies.pop(KB_AUTH_TOKEN)
                return None
        return None
