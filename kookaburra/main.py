import os
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware

from kookaburra import __version__
from kookaburra.api import gh_router, health_router, llm_router, sms_router
from kookaburra.auth import GitHubAuthBackend
from kookaburra.const import LOCAL_DOMAINS, ORIGINS
from kookaburra.exc import exception_handlers
from kookaburra.settings import env
from kookaburra.views import views

os.environ["TZ"] = "UTC"

app = FastAPI(
    title="🪶",
    version=__version__,
    exception_handlers=exception_handlers,
)

ORIGINS.extend(
    [
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
) if any(domain in env.KOOKABURRA_URL for domain in LOCAL_DOMAINS) else ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=env.API_SECRET_KEY,
)
app.add_middleware(
    AuthenticationMiddleware,
    backend=GitHubAuthBackend(),
)
app.mount(
    path="/static",
    app=StaticFiles(directory="static"),
    name="static",
)


app.include_router(health_router)
app.include_router(sms_router)
app.include_router(gh_router)
app.include_router(llm_router)
app.include_router(views)


@app.middleware("http")
async def add_process_time_header(
    request: Request,
    call_next: Callable,
) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Seconds"] = str(process_time)
    return response
