import requests
import urllib.parse
from .provider import Provider
from .auth.sign import RequestSigner

__all__ = ["DataClient"]


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

        response = requests.get(url, headers=headers)

        if response.status_code == 403 and self.request_signer:
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = requests.get(url, headers=headers)

        return response.json()

    def post(self, data: dict) -> dict:
        headers = self.provider.headers or {}
        url = self.provider.endpoint

        if self.request_signer:
            headers.update(self.request_signer.sign())

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 403 and self.request_signer:
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = requests.get(url, headers=headers)

        return response.json()

    def put(self, data: dict) -> dict:
        headers = self.provider.headers or {}
        url = self.provider.endpoint

        if self.request_signer:
            headers.update(self.request_signer.sign())

        response = requests.put(url, json=data, headers=headers)

        if response.status_code == 403 and self.request_signer:
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = requests.get(url, headers=headers)

        return response.json()

    def delete(self, params: dict) -> dict:
        query_params = urllib.parse.urlencode(params)
        url = f"{self.provider.endpoint}?{query_params}"
        headers = self.provider.headers or {}

        if self.request_signer:
            headers.update(self.request_signer.sign())

        response = requests.delete(url, headers=headers)

        if response.status_code == 403 and self.request_signer:
            self.request_signer.clear()
            headers.update(self.request_signer.sign())
            response = requests.get(url, headers=headers)

        return response.json()
