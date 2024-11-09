import os, json, logging, time
import requests

__all__ = ["TokenStore"]

Log = logging.getLogger("TokenStore")

app_name = os.getenv("APP_NAME")
creds_dir = os.path.expanduser(f"~/.{app_name}")
os.makedirs(creds_dir, exist_ok=True)


class TokenStore:

    def __init__(
        self, provider: str, client_id: str, client_secret: str, redirect_uri: str, token_endpoint: str
    ):
        self.provider = provider
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_endpoint = token_endpoint
        self.provider_file = os.path.join(creds_dir, f"{provider}.json")
        
        # Create path of file if it doesn't exist
        os.makedirs(os.path.dirname(self.provider_file), exist_ok=True)

    def save(self, token_data: dict):
        if not token_data.get("access_token"):
            Log.info(f"Access token is missing for provider {self.provider}.")
            raise ValueError("Access token is missing.")

        if "expires_in" in token_data:
            token_data["expires_at"] = int(time.time()) + token_data["expires_in"]

        with open(self.provider_file, "w") as file:
            json.dump(token_data, file)

        os.chmod(self.provider_file, 0o600)
        Log.info(f"Token saved successfully for provider {self.provider}.")

    def access_token(self):
        self.provider_file = os.path.join(creds_dir, f"{self.provider}.json")
        if not os.path.exists(self.provider_file):
            Log.info(f"No token found for provider {self.provider}.")
            return None

        with open(self.provider_file, "r") as file:
            token_data = json.load(file)

        if not token_data:
            Log.info(f"Token data is missing for provider {self.provider}.")
            return None

        if not token_data.get("access_token"):
            Log.info(f"Access token is missing for provider {self.provider}.")
            return None

        if "expires_at" in token_data:
            # if expires in 10 seconds, refresh token
            if token_data["expires_at"] - int(time.time()) < 10:
                token_data = self._refresh_access_token()
                if not token_data:
                    return None

                self.save(token_data)

        Log.info(f"Access token retrieved for provider {self.provider}.")
        return token_data["access_token"]

    def _refresh_access_token(self, token_data: dict) -> dict:
        Log.info(f"Refreshing token for provider {self.provider}.")
        with open(self.provider_file, "r") as file:
            token_data = json.load(file)

        if not token_data.get("refresh_token"):
            Log.info(f"Refresh token is missing for provider {self.provider}.")
            return None

        data = {
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"],
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }

        if token_data.get("scope"):
            data["scope"] = token_data["scope"]

        response = requests.post(self.token_endpoint, data=data)

        if response.status_code == 200:
            new_token_data = response.json()
            new_token_data["refresh_token"] = new_token_data.get(
                "refresh_token", token_data["refresh_token"]
            )
            return new_token_data
        else:
            Log.error(f"Failed to refresh token for provider {self.provider}.")
            return None

    def delete(self):
        self.provider_file = os.path.join(creds_dir, f"{self.provider}.json")
        if os.path.exists(self.provider_file):
            os.remove(self.provider_file)
            Log.info(f"Token deleted for provider {self.provider}.")
        else:
            Log.info(f"No token found for provider {self.provider}.")
