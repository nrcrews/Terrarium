import logging
from threading import Event
from .token import TokenStore
from .server import AuthServer, active_server
from .provider import ProviderAuthConfig


__all__ = ["RequestSigner"]


Log = logging.getLogger("RequestSigner")


class RequestSigner:

    def __init__(self, config: ProviderAuthConfig):
        self.config = config
        self.token_store = TokenStore(
            provider=config.id,
            client_id=config.client_id,
            client_secret=config.client_secret,
            redirect_uri=config.redirect_uri,
            token_endpoint=config.token_endpoint,
        )
        self.header = config.header
        self.token_prefix = config.token_prefix

    def sign(self) -> dict:
        access_token = self.token_store.access_token()
        if not access_token:
            token_received_event = Event()
            active_server.authorize(
                provider=self.config, 
                token_store=self.token_store,
                token_received_event=token_received_event
            )
            token_received_event.wait()
            access_token = self.token_store.access_token()

            if not access_token:
                Log.error("Failed to obtain access token.")
                raise ValueError("Failed to obtain access token.")

        return {self.header: f"{self.token_prefix}{access_token}"}

    def clear(self):
        self.token_store.delete()
        Log.info(f"Token cleared for provider {self.provider}.")
