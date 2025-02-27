import os
import shutil
import tempfile
import time
from typing import Dict

import httpx
import jwt
from git import Repo
from github import Github
from sqlmodel.ext.asyncio.session import AsyncSession

from kookaburra.const import _APP, KOOKABURRA_DEPLOY_PATH
from kookaburra.deployment import deploy_svc
from kookaburra.exc import KookaburraException
from kookaburra.llm import llm_svc
from kookaburra.models import GitHubUser
from kookaburra.settings import env
from kookaburra.twilio import twilio_svc
from kookaburra.types import GitHubToken, GitHubUserData


class GitHubService:  # pragma: no cover
    def get_github(self, token: GitHubToken) -> Github:
        return Github(login_or_token=token.access_token)

    async def get_gh_user_data(self, token: GitHubToken) -> GitHubUserData:
        _gh = self.get_github(token=token)
        _gh_user = _gh.get_user()
        return GitHubUserData(
            emails=[e._asdict() for e in _gh_user.get_emails()],
            raw_data=_gh_user.raw_data,
        )

    async def handle_webhook(
        self, request: Dict, headers: Dict, user: GitHubUser, psql: AsyncSession
    ) -> None:
        if await self.is_push(headers=headers):
            await self.handle_push(request=request, psql=psql, user=user)

    async def is_push(self, headers: Dict) -> bool:
        return headers.get("x-github-event", None) == "push"

    async def handle_push(
        self, request: Dict, psql: AsyncSession, user: GitHubUser
    ) -> None:
        await self.post_commit_status(
            full_name=request["repository"]["full_name"],
            sha=request["after"],
            state="pending",
            description="Deploying...",
        )
        try:
            # if the ref that recieved the push is the default branch, then
            # clone the content into kookaburra_deploy and run the deploy to modal
            ref = request["ref"]
            default_branch = await self.get_default_branch(request=request)
            if ref.endswith(default_branch):
                # in a temporary directory, clone the repo
                with tempfile.TemporaryDirectory() as tmpdir:
                    # copy kookaburra_deployment to the tmpdir
                    # clone the repo into the tmpdir
                    # run the deploy
                    to_path = os.path.join(tmpdir, KOOKABURRA_DEPLOY_PATH, _APP)
                    os.makedirs(to_path, exist_ok=True)
                    to_path = await self.clone_repo(request=request, to_path=to_path)
                    deploy_root = os.path.join(tmpdir, KOOKABURRA_DEPLOY_PATH)
                    # copy the app to the deploy root
                    shutil.copytree(
                        src=to_path,
                        dst=deploy_root,
                        dirs_exist_ok=True,
                    )
                    # remove the app from the deploy root
                    shutil.rmtree(to_path)
                    # copy the kookaburra_deployment to the deploy root
                    shutil.copytree(
                        src=KOOKABURRA_DEPLOY_PATH,
                        dst=deploy_root,
                        dirs_exist_ok=True,
                    )
                    llm = await llm_svc.get_by_clone_url(
                        clone_url=request["repository"]["clone_url"], psql=psql
                    )
                    if llm is None:
                        llm = await llm_svc.create(
                            clone_url=request["repository"]["clone_url"],
                            psql=psql,
                            user=user,
                            phone_number=twilio_svc.provision_phone_number(),
                        )
                    await deploy_svc.modal_deploy(
                        tmpdir=tmpdir,
                        llm_id=str(llm.id),
                    )
                    await self.post_commit_status(
                        full_name=request["repository"]["full_name"],
                        sha=request["after"],
                        state="success",
                        description="Deployed!",
                    )
        except Exception:
            await self.post_commit_status(
                full_name=request["repository"]["full_name"],
                sha=request["after"],
                state="failure",
                description="Failed to deploy.",
            )

    async def get_default_branch(self, request: Dict) -> str:
        return request["repository"]["default_branch"]

    async def clone_repo(self, request: Dict, to_path: str) -> str:
        clone_url = request["repository"]["clone_url"]
        full_name = request["repository"]["full_name"]
        jwt = self.make_private_app_cloner_jwt()
        installation_id = await self.get_installation_id(full_name=full_name, jwt=jwt)
        access_token = await self.get_access_token_for_app(
            installation_id=installation_id, jwt=jwt
        )
        clone_url = clone_url.replace(
            "https://", f"https://x-access-token:{access_token}@"
        )
        Repo.clone_from(url=clone_url, to_path=to_path)
        return to_path

    def make_private_app_cloner_jwt(self) -> str:
        with open(env.GH_APP_PRIVATE_KEY_PATH, "rb") as pem_file:
            signing_key = jwt.jwk_from_pem(pem_file.read())
        payload = {
            # Issued at time
            "iat": int(time.time()),
            # JWT expiration time (10 minutes maximum)
            "exp": int(time.time()) + 600,
            # GitHub App's identifier
            "iss": env.GH_APP_ID,
        }
        jwt_instance = jwt.JWT()
        return jwt_instance.encode(payload, signing_key, alg="RS256")

    async def get_installation_id(self, full_name: str, jwt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/app/installations",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {jwt}",
                },
            )
        installations = response.json()
        for installation in installations:
            if installation["account"]["login"] == full_name.split("/")[0]:
                return installation["id"]
        raise KookaburraException(f"No installation found for this repo {full_name}.")

    async def get_access_token_for_app(self, installation_id: str, jwt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {jwt}",
                },
            )
        return response.json()["token"]

    async def post_commit_status(
        self, full_name: str, sha: str, state: str, description: str
    ) -> None:
        jwt = self.make_private_app_cloner_jwt()
        installation_id = await self.get_installation_id(full_name=full_name, jwt=jwt)
        access_token = await self.get_access_token_for_app(
            installation_id=installation_id, jwt=jwt
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{full_name}/statuses/{sha}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {access_token}",
                },
                json={
                    "state": state,
                    "target_url": env.KOOKABURRA_URL,
                    "description": description,
                    "context": "kookaburra",
                },
            )
        return response.json()


gh_svc = GitHubService()
