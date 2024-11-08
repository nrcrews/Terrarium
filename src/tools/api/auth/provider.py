from pydantic import BaseModel
from typing import Optional
from enum import Enum

__all__ = ["ProviderAuthConfig", "OAuthType"]


class OAuthType(str, Enum):
    CLIENT_SECRET = "client_secret"
    PKCE = "pkce"


class ProviderAuthConfig(BaseModel):
    id: str
    type: OAuthType
    client_id: str
    client_secret: Optional[str]
    authorization_endpoint: str
    token_endpoint: str
    scope: str
    redirect_uri: str
    header: str
    token_prefix: str
