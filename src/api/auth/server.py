import logging
import base64
import hashlib
import secrets
from threading import Event, Thread
import webbrowser
import urllib.parse
import requests
from flask import Flask, request
from .token import TokenStore


__all__ = ["AuthServer"]

Log = logging.getLogger("AuthServer")


class AuthServer:

    def __init__(
        self,
        provider: str,
        client_id: str,
        authorization_endpoint: str,
        token_endpoint: str,
        scope: str,
        redirect_uri: str,
        token_store: TokenStore
    ):
        self.provider = provider
        self.client_id = client_id
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.token_store = token_store

        self.app = Flask(__name__)
        self.state = secrets.token_urlsafe(32)
        self.code_verifier = None
        self.token_received_event = None
        self.access_token = None

        @self.app.route("/callback")
        def oauth_callback():
            global access_token
            error = request.args.get("error")
            if error:
                Log.error(f"Error during OAuth authorization")
                return (
                    "Authentication failed. Please check the console for details.",
                    400,
                )

            received_state = request.args.get("state")
            if received_state != self.state:
                Log.error("State parameter mismatch. Potential CSRF attack.")
                return "Invalid state parameter.", 400

            code = request.args.get("code")
            if not code:
                Log.error("No authorization code received.")
                return "Authorization code not found.", 400

            token_data = self._exchange_code_for_token(code)
            if token_data:
                self.token_store.save(token_data)
                access_token = token_data.get("access_token")
                self.token_received_event.set()
                self._shutdown_server()
                return "Authentication successful! You may close this window."
            else:
                return "Failed to obtain access token.", 400

    def _generate_pkce_pair(self):
        global code_verifier
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )
        return code_challenge

    def start(self, token_received_event: Event):
        self.token_received_event = token_received_event
        code_challenge = self._generate_pkce_pair()
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": self.state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{self.authorization_endpoint}?{urllib.parse.urlencode(params)}"

        # Start the Flask server in a separate thread
        Thread(target=self._run_flask_server).start()

        # Open the browser to start the OAuth flow
        webbrowser.open(auth_url)
        Log.info("Browser opened for OAuth authorization.")

    def _run_flask_server(self):
        self.app.run(port=5000, host="127.0.0.1")

    def _shutdown_server():
        func = request.environ.get("werkzeug.server.shutdown")
        if func:
            func()
        else:
            Log.error("Failed to shutdown server.")

    def _exchange_code_for_token(self, code: str):
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "code_verifier": code_verifier,
            # 'client_secret': CLIENT_SECRET,  # Do not include for public clients
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.token_endpoint, data=data, headers=headers)

        if response.status_code == 200:
            token_data = response.json()
            return token_data
        else:
            Log.error(f"Failed to exchange code for token")
            Log.error(response.status_code)
            Log.error(response.text)
            return None
