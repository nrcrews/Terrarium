import os, json
from typing import override
from ..tool import Tool
from .api import Provider, DataClient
from .api.auth.provider import ProviderAuthConfig, AuthType

__all__ = ["GetNews"]


class GetNews(Tool):

    @override
    @classmethod
    def name(self) -> str:
        return "get_news"

    @override
    @property
    def obj(self) -> dict:
        return {
            "name": GetNews.name(),
            "description": "Get news articles with descriptions and URLs.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for.",
                    },
                },
                "additionalProperties": False,
                "required": ["query"],
            },
        }

    @override
    def call(self, args: dict) -> str:
        query = args["query"]

        news_provider = Provider(
            id="news",
            name="News",
            auth_config=ProviderAuthConfig(
                id="news",
                type=AuthType.API_KEY,
                client_id=None,
                client_secret=None,
                api_key=os.getenv("NEWS_API_KEY"),
                authorization_endpoint=None,
                token_endpoint=None,
                scope=None,
                redirect_uri=None,
                header="Authorization",
                token_prefix="",
            ),
            endpoint=f"https://newsapi.org/v2/top-headlines",
            headers={},
        )

        client = DataClient(provider=news_provider)

        response = client.get({"q": query})
        return json.dumps(response)
