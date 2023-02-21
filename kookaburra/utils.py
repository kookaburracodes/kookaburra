import base64
import json
from typing import Callable, Union
from uuid import uuid4

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import Request, Response
from fastapi.routing import APIRoute

from kookaburra.log import log
from kookaburra.settings import env
from kookaburra.types import (
    JsonResponseLoggerMessage,
    RequestLoggerMessage,
    ResponseLoggerMessage,
)

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=env.API_SALT.encode("utf8"),
    iterations=390_000,
)
_deriv = kdf.derive(env.API_SECRET_KEY.encode("utf8"))
_fernet = Fernet(base64.urlsafe_b64encode(_deriv))


def _encrypt(data: bytes) -> bytes:
    return _fernet.encrypt(data)


def _decrypt(data: str) -> bytes:
    return _fernet.decrypt(data)


class _APIRoute(APIRoute):
    """_APIRoute.

    _APIRoute is a custom APIRoute class that adds a background task to the
    response to log request and response data.
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def _log(
            req: RequestLoggerMessage,
            res: Union[JsonResponseLoggerMessage, ResponseLoggerMessage],
        ) -> None:
            id = {"id": str(uuid4()).replace("-", "")}
            log.debug({**json.loads(req.json()), **id})
            log.debug({**json.loads(res.json()), **id})

        async def custom_route_handler(request: Request) -> Response:
            req = RequestLoggerMessage(**request.__dict__)
            response = await original_route_handler(request)
            # if the response headers contain a content-type of application/json
            # then log the response body
            res: Union[JsonResponseLoggerMessage, ResponseLoggerMessage]
            if response.headers.get("content-type") == "application/json":
                res = JsonResponseLoggerMessage(**response.__dict__)
            else:
                res = ResponseLoggerMessage(**response.__dict__)
            await _log(req=req, res=res)
            return response

        return custom_route_handler
