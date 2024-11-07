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
        url = f"{self.provider.base_url}?{query_params}"
        headers = self.provider.headers or {}
        
        if self.request_signer:
            headers.update(self.request_signer.sign())
            
        response = requests.get(url, headers=headers)
        return response.json()

    def post(self, data: dict) -> dict:
        headers = self.provider.headers or {}
        
        if self.request_signer:
            headers.update(self.request_signer.sign())
            
        response = requests.post(self.provider.base_url, json=data, headers=headers)
        return response.json()

    def put(self, data: dict) -> dict:
        headers = self.provider.headers or {}
        
        if self.request_signer:
            headers.update(self.request_signer.sign())
            
        response = requests.put(self.provider.base_url, json=data, headers=headers)
        return response.json()

    def delete(self, params: dict) -> dict:
        query_params = urllib.parse.urlencode(params)
        url = f"{self.provider.base_url}?{query_params}"
        headers = self.provider.headers or {}
        
        if self.request_signer:
            headers.update(self.request_signer.sign())
            
        response = requests.delete(url, headers=headers)
        return response.json()
