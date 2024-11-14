import logging
import requests
import requests_cache
from retry_requests import retry

import urllib.parse
from .provider import Provider
from .auth.sign import RequestSigner

__all__ = ["DataClient"]

Log = logging.getLogger("DataClient")

cache_session = requests_cache.CachedSession('.cache', expire_after = 300)
retry_session = retry(cache_session, retries = 3, backoff_factor = 0.2)

class DataClient:

    def __init__(self, provider: Provider):
        self.provider = provider
        if provider.auth_config:
            self.request_signer = RequestSigner(provider.auth_config)

    def get(self, params: dict) -> dict:
        query_params = urllib.parse.urlencode(params)
        url = f"{self.provider.endpoint}?{query_params}"
        headers = self.provider.headers or {}

        if self.request_signer:
            headers.update(self.request_signer.sign())

        response = retry_session.get(url, headers=headers)

        if response.status_code == 403 and self.request_signer:
            Log.info("Token expired. Refreshing token.")
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = retry_session.get(url, headers=headers)

        if not response.ok:
            Log.error(f"Failed to get data from {self.provider.id}")
            return

        return response.json()

    def post(self, data: dict) -> dict:
        headers = self.provider.headers or {}
        url = self.provider.endpoint

        if self.request_signer:
            headers.update(self.request_signer.sign())

        response = retry_session.post(url, json=data, headers=headers)

        if response.status_code == 403 and self.request_signer:
            Log.info("Token expired. Refreshing token.")
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = retry_session.post(url, json=data, headers=headers)

        if not response.ok:
            Log.error(f"Failed to get data from {self.provider.id}")
            return

        return response.json()

    def put(self, data: dict) -> dict:
        headers = self.provider.headers or {}
        url = self.provider.endpoint

        if self.request_signer:
            headers.update(self.request_signer.sign())

        response = retry_session.put(url, json=data, headers=headers)

        if response.status_code == 403 and self.request_signer:
            Log.info("Token expired. Refreshing token.")
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = retry_session.put(url, json=data, headers=headers)

        if not response.ok:
            Log.error(f"Failed to get data from {self.provider.id}")
            return

        return response.json()

    def delete(self, params: dict) -> dict:
        query_params = urllib.parse.urlencode(params)
        url = f"{self.provider.endpoint}?{query_params}"
        headers = self.provider.headers or {}

        if self.request_signer:
            headers.update(self.request_signer.sign())

        response = retry_session.delete(url, headers=headers)

        if response.status_code == 403 and self.request_signer:
            Log.info("Token expired. Refreshing token.")
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = retry_session.delete(url, headers=headers)

        if not response.ok:
            Log.error(f"Failed to get data from {self.provider.id}")
            return

        return response.json()
