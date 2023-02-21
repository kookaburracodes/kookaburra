from datetime import timedelta

API_V0 = "/api/v0"

ORIGINS = [
    "https://app.kookaburra.codes",
    "https://kookaburra.codes",
    "https://github.com",
]
LOCAL_DOMAINS = [
    "localhost",
    "127.0.0.1",
]
KOOKABURRA_DEPLOY_PATH = "kookaburra_deployment"
MODAL_STUB_FILE = "_modal.py"
MODAL_API = "api.modal.run"
_APP = "_app"

MODAL_ACCOUNT_NAME = "kookaburracodes"

KB_AUTH_TOKEN = "kb_auth_token"

KB_AUTH_TOKEN_EXPIRE_SECONDS = timedelta(seconds=60 * 60 * 24 * 2)
