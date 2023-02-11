import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from kookaburra import __version__
from kookaburra.api import gh_router, health_router, sms_router
from kookaburra.const import LOCAL_DOMAINS, ORIGINS
from kookaburra.settings import env

os.environ["TZ"] = "UTC"

app = FastAPI(
    title="🪶",
    version=__version__,
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

app.include_router(health_router)
app.include_router(sms_router)
app.include_router(gh_router)
