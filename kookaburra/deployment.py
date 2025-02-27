import os

import sh
from modal.cli.run import deploy

from kookaburra.const import (
    KOOKABURRA_DEPLOY_PATH,
    MODAL_ACCOUNT_NAME,
    MODAL_API,
    MODAL_STUB_FILE,
)
from kookaburra.settings import env


class DeploymentService:  # pragma: no cover
    async def modal_deploy(self, tmpdir: str, llm_id: str) -> None:
        sh.modal(
            "token",
            "set",
            "--token-id",
            env.MODAL_TOKEN_ID,
            "--token-secret",
            env.MODAL_TOKEN_SECRET,
            _out="/tmp/modal_token_set.log",
            _new_session=False,
        )
        pwd = os.getcwd()
        os.chdir(tmpdir)
        deploy(
            stub_ref=f"{KOOKABURRA_DEPLOY_PATH}/{MODAL_STUB_FILE}",
            name=llm_id,
        )
        os.chdir(pwd)

    def get_modal_url(self, llm_id: str) -> str:
        return f"https://{MODAL_ACCOUNT_NAME}--{llm_id}--{MODAL_API}/"

    async def stop_modal_app(self, llm_id: str) -> None:
        sh.modal(
            "app",
            "stop",
            "--name",
            llm_id,
            _out="/tmp/modal_app_stop.log",
            _new_session=False,
        )


deploy_svc = DeploymentService()
