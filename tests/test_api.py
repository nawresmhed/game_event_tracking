"""
Unit tests for the SDK client.

Verifies that the SDK correctly builds request payloads,
sets authorization headers, and targets the expected API endpoints
without making real HTTP requests.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from sdk import GameEventClient, GameEventClientConfig, InstallEvent

class DummyResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

def test_sdk_builds_payload():
    client = GameEventClient(GameEventClientConfig(base_url="https://example.com", api_key="k"))
    captured = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return DummyResponse(200)

    client._session.post = fake_post

    ev = InstallEvent.create(player_id="p1", app_id="app", platform="ios")
    resp = client.send_install(ev)

    assert resp.status_code == 200
    assert captured["url"].endswith("/v1/events/install")
    assert captured["json"]["event_type"] == "install"
    assert captured["headers"]["Authorization"] == "Bearer k"
