from pathlib import Path
from typing import List

import modal
from fastapi import FastAPI

from kookaburra_deployment.main import app

stub = modal.Stub()

DEFAULT_PIP_INSTALL = [
    "fastapi",
    "langchain",
    "openai",
]

DEPLOY_ROOT = "kookaburra_deployment"
DEFAULT_REQUIREMENTS_PATH = f"{DEPLOY_ROOT}/requirements.txt"
DEFAULT_APT_INSTALL_PATH = f"{DEPLOY_ROOT}/apt_install.txt"
DEFAULT_PYPROJECT_PATH = f"{DEPLOY_ROOT}/pyproject.toml"


def _read_lines_from_file(path: str) -> list:
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]


APT_PACKAGES_TO_INSTALL = []
if Path(DEFAULT_APT_INSTALL_PATH).exists():
    APT_PACKAGES_TO_INSTALL = _read_lines_from_file(DEFAULT_APT_INSTALL_PATH)


def _make_mounts() -> List[modal.Mount]:
    mounts = []
    for path in Path(".").glob("**/*"):
        if path.is_dir() and path.name not in ["__pycache__"]:
            mounts.append(
                modal.Mount(
                    local_dir=path.absolute(),
                    remote_dir=f"/root/{path}".replace(DEPLOY_ROOT, ""),
                )
            )
    return mounts


if Path(DEFAULT_REQUIREMENTS_PATH).exists():
    image = (
        modal.Image.debian_slim()
        .apt_install(APT_PACKAGES_TO_INSTALL)
        .pip_install(DEFAULT_PIP_INSTALL)
        .pip_install_from_requirements(
            requirements_txt=DEFAULT_REQUIREMENTS_PATH,
        )
    )
elif Path(DEFAULT_PYPROJECT_PATH).exists():
    image = (
        modal.Image.debian_slim()
        .apt_install(APT_PACKAGES_TO_INSTALL)
        .pip_install(DEFAULT_PIP_INSTALL)
        .pip_install_from_pyproject(
            pyproject_toml=DEFAULT_PYPROJECT_PATH,
        )
    )
else:
    image = (
        modal.Image.debian_slim()
        .apt_install(APT_PACKAGES_TO_INSTALL)
        .pip_install(DEFAULT_PIP_INSTALL)
    )


@stub.asgi(
    image=image,
    secret=modal.Secret.from_name("kb-openai-api-key"),
    mounts=_make_mounts(),
)
def _api() -> FastAPI:
    return app


if __name__ == "__main__":
    stub.serve()
