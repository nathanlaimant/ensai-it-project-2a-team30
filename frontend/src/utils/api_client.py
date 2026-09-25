import os
from typing import Any, Optional
import requests

class APIClient:
    def __init__(self, base_url: str = None, timeout: int = 10):
        default_url = os.getenv("API_BASE_URL", "http://localhost:5000")
        self.base_url = (base_url or default_url).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        """Assure la jointure """
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else {}

    def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        url = self._build_url(endpoint)
        response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else {}

    def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Any:
        url = self._build_url(endpoint)
        response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else {}

    def delete(
        self,
        endpoint: str,
        headers: Optional[dict[str, str]] = None,
    ) -> int:
        url = self._build_url(endpoint)
        response = self.session.delete(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.status_code