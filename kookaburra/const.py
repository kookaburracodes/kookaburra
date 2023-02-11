HTTPIMPORT_INI_TEMPLATE = """
[github]
headers:
  Authorization: token {token}
""".strip()

API_V0 = "/api/v0"

ORIGINS = [
    "https://kookaburra.codes",
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
