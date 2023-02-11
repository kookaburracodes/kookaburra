import modal
from fastapi import FastAPI

from kookaburra_deployment.main import app

stub = modal.Stub()

# TODO: extend this to support user specified packages
# take pyproject.toml or requirements.txt as input
# and install the globally unique set of these packages
# and the prod dependencies of a pyproject or the contents of
# requirements.txt
# this should happen in the gh_svc.handle_push function
image = modal.Image.debian_slim().pip_install(
    [
        "fastapi >=0.70.0",
        "langchain >=0.0.50",
        "openai >=0.6.0",
    ]
)


@stub.asgi(
    image=image,
    secret=modal.Secret.from_name("kb-openai-api-key"),
)
def _api() -> FastAPI:
    return app


if __name__ == "__main__":
    stub.serve()
