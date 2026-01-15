"""
Unit tests for the SDK HTTP client.
Ensures that the SDK correctly builds HTTP requests for game events,
including endpoint paths, payload serialization, authorization headers,
and timeout configuration, without making real network calls.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from sdk import GameEventClient, GameEventClientConfig, InstallEvent


class DummyResponse:
    def __init__(self, status_code=200, text="OK"):
        self.status_code = status_code
        self.text = text


def test_sdk_builds_payload():
    client = GameEventClient(
        GameEventClientConfig(base_url="https://example.com", api_key="k")
    )
    captured = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return DummyResponse(200)

    # patch
    original_post = client._session.post
    client._session.post = fake_post  # type: ignore
    try:
        ev = InstallEvent.create(player_id="p1", app_id="app", platform="ios")
        resp = client.send_install(ev)

        assert resp.status_code == 200
        assert captured["url"].endswith("/v1/events/install")
        assert captured["json"]["event_type"] == "install"
        assert captured["headers"]["Authorization"] == "Bearer k"
        assert captured["headers"]["Content-Type"] == "application/json"
        assert captured["timeout"] == client.config.timeout_seconds
    finally:
        # restore
        client._session.post = original_post
