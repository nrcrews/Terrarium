import logging, base64, hashlib, secrets
from threading import Event, Thread
import webbrowser
import urllib.parse
import requests
from flask import Flask, request
from .token import TokenStore
from .provider import OAuthType, ProviderAuthConfig


__all__ = ["AuthServer", "active_server"]

Log = logging.getLogger("AuthServer")


class AuthServer:

    def __init__(self):
        self.app = Flask(__name__)
        self.token_received_events: dict[str, Event] = {}
        self.states: dict[str, str] = {}
        self.providers: dict[str, ProviderAuthConfig] = {}
        self.token_stores: dict[str, TokenStore] = {}
        self.code_verifiers: dict[str, str] = {}

        self.app.add_url_rule(
            "/<provider>/callback",
            "oauth_callback",
            self.oauth_callback,
            methods=["GET"],
        )

    def start(self):
        self.app.run(port=5000, host="127.0.0.1")

    def oauth_callback(self, provider: str):
        error = request.args.get("error")
        if error:
            Log.error(f"Error during OAuth authorization")
            self._cleanup(provider)
            return (
                "Authentication failed. Please check the console for details.",
                400,
            )

        received_state = request.args.get("state")
        if received_state != self.states.get(provider):
            Log.error("State parameter mismatch. Potential CSRF attack.")
            self._cleanup(provider)
            return "Invalid state parameter.", 400

        code = request.args.get("code")
        if not code:
            Log.error("No authorization code received.")
            self._cleanup(provider)
            return "Authorization code not found.", 400

        token_data = self._exchange_code_for_token(provider, code)
        if token_data:
            if self.token_stores.get(provider) is None:
                Log.error(f"Token store not found for provider {provider}.")
            else:
                self.token_stores[provider].save(token_data)
            self.token_received_events[provider].set()
            self._cleanup(provider)
            return "Authentication successful! You may close this window."
        else:
            self._cleanup(provider)
            return "Failed to obtain access token.", 400

    def _generate_pkce_pair(self, provider: str):
        code_verifier = secrets.token_urlsafe(64)
        self.code_verifiers[provider] = code_verifier
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )
        return code_challenge

    def _exchange_code_for_token(self, provider_id: str, code: str):
        provider = self.providers[provider_id]
        if provider.type == OAuthType.CLIENT_SECRET:
            data = {
                "code": code,
                "redirect_uri": provider.redirect_uri,
                "client_id": provider.client_id,
                "client_secret": provider.client_secret,
            }
        elif provider.type == OAuthType.PKCE:
            data = {
                "code": code,
                "redirect_uri": provider.redirect_uri,
                "client_id": provider.client_id,
                "code_verifier": provider.code_verifiers[provider.id],
            }
        else:
            raise ValueError("Invalid OAuth type.")

        headers = {"Accept": "application/json"}
        response = requests.post(provider.token_endpoint, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            return token_data
        else:
            Log.error(f"Failed to exchange code for token")
            Log.error(response.status_code)
            Log.error(response.text)
            return None

    def _cleanup(self, provider: str):
        try:
            self.states.pop(provider)
            self.providers.pop(provider)
            self.code_verifiers.pop(provider)
            self.token_stores.pop(provider)
            self.token_received_events.pop(provider)
        except KeyError:
            Log.error("Failed to clean up OAuth state.")

    def authorize(
        self,
        provider: ProviderAuthConfig,
        token_store: TokenStore,
        token_received_event: Event,
    ):
        self.token_received_events[provider.id] = token_received_event
        state = secrets.token_urlsafe(32)
        self.states[provider.id] = state
        self.providers[provider.id] = provider
        self.token_stores[provider.id] = token_store

        if provider.type == OAuthType.CLIENT_SECRET:
            params = {
                "client_id": provider.client_id,
                "response_type": "code",
                "redirect_uri": provider.redirect_uri,
                "scope": provider.scope,
                "state": state,
            }
        elif provider.type == OAuthType.PKCE:
            code_challenge = self._generate_pkce_pair(provider=provider.id)
            params = {
                "client_id": provider.client_id,
                "response_type": "code",
                "redirect_uri": provider.redirect_uri,
                "scope": provider.scope,
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
        else:
            self._cleanup(provider)
            raise ValueError("Invalid OAuth type.")
        auth_url = f"{provider.authorization_endpoint}?{urllib.parse.urlencode(params)}"

        webbrowser.open(auth_url)
        Log.info("Browser opened for OAuth authorization.")


# Start the server
Log.info("Starting OAuth server.")
active_server = AuthServer()
Thread(target=active_server.start, daemon=True).start()
