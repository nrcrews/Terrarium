from threading import Event
from .token import TokenStore
from .server import AuthServer
from .provider import ProviderAuthConfig

__all__ = ["RequestSigner"]


class RequestSigner:

    def __init__(self, config: ProviderAuthConfig):
        self.token_store = TokenStore(
            provider=config.id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            redirect_uri=config.redirect_uri,
            token_endpoint=config.token_endpoint,
        )
        self.auth_server = AuthServer(
            provider=config.id,
            auth_type=config.type,
            client_id=config.client_id,
            client_secret=config.client_secret,
            authorization_endpoint=config.authorization_endpoint,
            token_endpoint=config.token_endpoint,
            scope=config.scope,
            redirect_uri=config.redirect_uri,
            token_store=self.token_store,
        )
        self.header = config.header
        self.token_prefix = config.token_prefix

    def sign(self) -> dict:
        access_token = self.token_store.access_token()
        if not access_token:
            token_received_event = Event()
            self.auth_server.start(token_received_event)
            token_received_event.wait()
            access_token = self.token_store.access_token()

            if not access_token:
                raise ValueError("Failed to obtain access token.")

        return {self.header: f"{self.token_prefix}{self.token_store.access_token()}"}
