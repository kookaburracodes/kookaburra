from typing import List, Mapping


class MockGithubEmail:
    def _asdict(
        self,
    ) -> dict:
        return {
            "email": "user@example.com",
            "primary": True,
            "verified": True,
            "visibility": "visibility",
        }


class MockGithubUser:
    @staticmethod
    def get_emails() -> list[MockGithubEmail]:
        return [MockGithubEmail()]

    @property
    def raw_data(self) -> dict:
        return {
            "login": "login",
            "id": 1,
            "node_id": "node_id",
            "avatar_url": "avatar_url",
            "gravatar_id": "gravatar_id",
            "url": "url",
            "html_url": "html_url",
            "followers_url": "followers_url",
            "following_url": "following_url",
            "gists_url": "gists_url",
            "starred_url": "starred_url",
            "subscriptions_url": "subscriptions_url",
            "organizations_url": "organizations_url",
            "repos_url": "repos_url",
            "events_url": "events_url",
            "received_events_url": "received_events_url",
            "type": "type",
            "site_admin": False,
            "name": "name",
            "company": "company",
            "blog": "blog",
            "location": "location",
            "email": "email",
            "hireable": False,
            "bio": "bio",
            "twitter_username": "twitter_username",
            "public_repos": 1,
            "public_gists": 1,
            "followers": 1,
            "following": 1,
            "created_at": "created_at",
            "updated_at": "updated_at",
        }


class MockGithub:
    @staticmethod
    def get_user() -> MockGithubUser:
        return MockGithubUser()


class MockAsyncOAuth2Client:
    @staticmethod
    async def fetch_token(
        url: str,
        authorization_response: str,
    ) -> Mapping:
        return {
            "access_token": "access_token",
            "token_type": "token_type",
            "scope": "scope",
        }


class MockGoogleCloudStorageBlob:
    @staticmethod
    def download_as_string() -> str:
        return '{"_in": "message", "_out": "message", "timestamp": 0}'

    @staticmethod
    def upload_from_string(data: str) -> None:
        pass


class MockGoogleCloudStorageBucket:
    @staticmethod
    def list_blobs(prefix: str) -> List:
        return [MockGoogleCloudStorageBlob(), MockGoogleCloudStorageBlob()]

    @staticmethod
    def blob(path: str) -> MockGoogleCloudStorageBlob:
        return MockGoogleCloudStorageBlob()


class MockGoogleCloudStorageClient:
    @staticmethod
    def get_bucket(bucket_or_name: str) -> MockGoogleCloudStorageBucket:
        return MockGoogleCloudStorageBucket()
