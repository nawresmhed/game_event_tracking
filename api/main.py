"""
FastAPI application for ingesting game install and purchase events.

Validates and authenticates incoming events, performs basic deduplication,
and forwards events to AWS Kinesis Firehose (or a mock implementation).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import InstallEventIn, PurchaseEventIn, EventAccepted
from .firehose_client import FirehoseClient, FirehoseConfig

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="Game Event Tracking API", version="0.1.0")

# --- Config
API_KEY = os.getenv("EVENT_API_KEY")  # if unset -> auth disabled (dev mode)
FIREHOSE_STREAM = os.getenv("FIREHOSE_STREAM_NAME", "example-game-events")
AWS_REGION = os.getenv("AWS_REGION")
MOCK_FIREHOSE = os.getenv("MOCK_FIREHOSE", "false").lower() == "true"

security = HTTPBearer(auto_error=False)

def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> None:
    """
    Dependency that enforces Bearer token authentication.
    Rejects requests with missing or invalid Authorization headers
    when an API key is configured.
    """
    if not API_KEY:
        return  # auth disabled

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme (expected Bearer)")

    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# --- Firehose (mock)
class MockFirehose:
    """
        Mock Firehose client.
        Prints events instead of sending them to AWS Kinesis Firehose.
        """
    def put_event(self, event: dict) -> None:
        print("[MOCK_FIREHOSE] would send:", event)

firehose = (
    MockFirehose()
    if MOCK_FIREHOSE
    else FirehoseClient(FirehoseConfig(delivery_stream_name=FIREHOSE_STREAM, region_name=AWS_REGION))
)

_seen_event_ids: set[str] = set()

def _dedupe(event_id: str) -> bool:
    """
    Checks whether an event has already been processed.

    Returns True if the event_id is a duplicate, otherwise records it
    and returns False.
    """
    if event_id in _seen_event_ids:
        return True
    _seen_event_ids.add(event_id)
    return False

print(
    f"[startup] MOCK_FIREHOSE={MOCK_FIREHOSE} AWS_REGION={AWS_REGION} "
    f"FIREHOSE_STREAM={FIREHOSE_STREAM} AUTH_ENABLED={bool(API_KEY)}"
)

@app.get("/health")
def health():
    """
        Health check endpoint used to verify service availability.
        """
    return {"status": "ok"}

@app.post("/v1/events/install", response_model=EventAccepted)
def ingest_install(
    event: InstallEventIn,
    _: None = Depends(verify_api_key),
):
    """
        Ingests a game install event.

        Validates the event, applies deduplication, and forwards it
        to the configured Firehose delivery stream.
        """
    if _dedupe(event.event_id):
        return EventAccepted(event_id=event.event_id)

    payload: Dict[str, Any] = event.model_dump()
    payload["received_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"

    firehose.put_event(payload)
    return EventAccepted(event_id=event.event_id)

@app.post("/v1/events/purchase", response_model=EventAccepted)
def ingest_purchase(
    event: PurchaseEventIn,
    _: None = Depends(verify_api_key),
):
    """
       Ingests a game purchase event.

       Validates the event, applies deduplication, and forwards it
       to the configured Firehose delivery stream.
       """
    if _dedupe(event.event_id):
        return EventAccepted(event_id=event.event_id)

    payload: Dict[str, Any] = event.model_dump()
    payload["received_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"

    firehose.put_event(payload)
    return EventAccepted(event_id=event.event_id)
