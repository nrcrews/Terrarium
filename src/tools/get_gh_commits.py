import os, json
from typing import override
from ..tool import Tool
from .api import Provider, DataClient
from .api.auth.provider import ProviderAuthConfig, OAuthType

__all__ = ["GetGitHubCommits"]


class GetGitHubCommits(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "get_github_commits"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": GetGitHubCommits.name(),
            "description": "Get the commits of a GitHub repository.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "The repository to get the commits from.",
                    },
                    "since": {
                        "type": "string",
                        "description": "Only commits after this date will be returned. Format: YYYY-MM-DDTHH:MM:SSZ",
                    },
                },
                "additionalProperties": False,
                "required": ["repo", "since"],
            },
        }

    @override
    def call(self, args: dict) -> str:
        repo = args["repo"]
        since = args["since"]

        gh_provider = Provider(
            id="github",
            name="GitHub",
            auth_config=ProviderAuthConfig(
                id="github",
                type=OAuthType.CLIENT_SECRET,
                client_id=os.getenv("GITHUB_CLIENT_ID"),
                client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
                authorization_endpoint="https://github.com/login/oauth/authorize",
                token_endpoint="https://github.com/login/oauth/access_token",
                scope="repo",
                redirect_uri="http://127.0.0.1:5000/github/callback",
                header="Authorization",
                token_prefix="Bearer ",
            ),
            endpoint=f"https://api.github.com/repos/{repo}/commits",
            headers={
                "X-GitHub-Api-Version": "2022-11-28",
                "Accept": "application/vnd.github+json",
            },
        )

        client = DataClient(provider=gh_provider)

        response = client.get({"since": since})
        return json.dumps(response)
