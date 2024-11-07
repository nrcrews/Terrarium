from threading import Event
from .token import TokenStore
from .server import AuthServer
from .provider import ProviderAuthConfig

__all__ = ["RequestSigner"]


class RequestSigner:

    def __init__(self, config: ProviderAuthConfig, header: str = "Authorization"):
        self.token_store = TokenStore(
            config.id, config.client_id, config.redirect_uri, config.token_endpoint
        )
        self.auth_server = AuthServer(
            config.id,
            config.client_id,
            config.authorization_endpoint,
            config.token_endpoint,
            config.scope,
            config.redirect_uri,
            self.token_store,
        )
        self.header = header

    def sign(self) -> dict:
        access_token = self.token_store.access_token()
        if not access_token:
            token_received_event = Event()
            self.auth_server.start(token_received_event)
            token_received_event.wait()
            access_token = self.token_store.access_token()

            if not access_token:
                raise ValueError("Failed to obtain access token.")

        return {self.header: f"Bearer {self.token_store.access_token()}"}
