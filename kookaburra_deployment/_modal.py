from pathlib import Path

import modal
from fastapi import FastAPI

from kookaburra_deployment.main import app

stub = modal.Stub()

DEFAULT_PIP_INSTALL = [
    "fastapi",
    "langchain",
    "openai",
]

DEFAULT_REQUIREMENTS_PATH = "requirements.txt"
DEFAULT_APT_INSTALL_PATH = "apt_install.txt"
DEFAULT_PYPROJECT_PATH = "pyproject.toml"


def _read_lines_from_file(path: str) -> list:
    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]


APT_PACKAGES_TO_INSTALL = []
if Path(DEFAULT_APT_INSTALL_PATH).exists():
    APT_PACKAGES_TO_INSTALL = _read_lines_from_file(DEFAULT_APT_INSTALL_PATH)


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
)
def _api() -> FastAPI:
    return app


if __name__ == "__main__":
    stub.serve()
