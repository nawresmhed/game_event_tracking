"""
Python SDK client for sending game events to the ingestion API.

Provides a simple interface for creating and sending install and
purchase events with automatic authentication and retry handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .events import BaseEvent, InstallEvent, PurchaseEvent

@dataclass(frozen=True)
class GameEventClientConfig:
    """
    Configuration object for the game event SDK client.

    Defines API endpoint settings, authentication, and retry behavior.
    """
    base_url: str
    api_key: Optional[str] = None
    timeout_seconds: float = 5.0
    max_retries: int = 3
    backoff_factor: float = 0.5

class GameEventClient:
    """
    SDK client for sending game events to the ingestion API.

    Manages HTTP communication, retries, timeouts, and authorization
    when sending install and purchase events.
    """
    def __init__(self, config: GameEventClientConfig):
        self.config = config
        self._session = requests.Session()

        retry = Retry(
            total=config.max_retries,
            backoff_factor=config.backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["POST"]),
            raise_on_status=False,
        )
        self._session.mount("http://", HTTPAdapter(max_retries=retry))
        self._session.mount("https://", HTTPAdapter(max_retries=retry))

    def send_install(self, event: InstallEvent) -> requests.Response:
        return self._post("/v1/events/install", event)

    def send_purchase(self, event: PurchaseEvent) -> requests.Response:
        return self._post("/v1/events/purchase", event)

    def send_event(self, event: Union[InstallEvent, PurchaseEvent, BaseEvent]) -> requests.Response:
        if event.event_type == "install":
            return self.send_install(event)
        if event.event_type == "purchase":
            return self.send_purchase(event)
        return self._post("/v1/events", event)

    def _post(self, path: str, event: BaseEvent) -> requests.Response:
        url = self.config.base_url.rstrip("/") + path
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return self._session.post(url, json=event.to_dict(), headers=headers, timeout=self.config.timeout_seconds)
