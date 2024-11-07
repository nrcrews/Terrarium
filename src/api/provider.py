from typing import Optional
from pydantic import BaseModel
from .auth.provider import ProviderAuthConfig

__all__ = ['Provider']

class Provider(BaseModel):
    id: str
    name: str
    auth_config: Optional[ProviderAuthConfig]
    endpoint: str
    headers: dict
    