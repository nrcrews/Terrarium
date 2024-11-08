from pydantic import BaseModel

__all__ = ["ProviderAuthConfig"]


class ProviderAuthConfig(BaseModel):
    id: str
    client_id: str
    authorization_endpoint: str
    token_endpoint: str
    scope: str
    redirect_uri: str
