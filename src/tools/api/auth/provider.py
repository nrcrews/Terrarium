from pydantic import BaseModel
from typing import Optional
from enum import Enum

__all__ = ["ProviderAuthConfig", "AuthType"]


class AuthType(str, Enum):
    OAUTH_CLIENT_SECRET = "oauth_client_secret"
    OAUTH_PKCE = "oauth_pkce"
    API_KEY = "api_key"


class ProviderAuthConfig(BaseModel):
    id: str
    type: AuthType
    client_id: Optional[str]
    client_secret: Optional[str]
    api_key: Optional[str]
    authorization_endpoint: Optional[str]
    token_endpoint: Optional[str]
    scope: Optional[str]
    redirect_uri: Optional[str]
    header: str = "Authorization"
    token_prefix: str = ""
