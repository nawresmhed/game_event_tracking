"""
Pydantic models defining the schema for incoming game events.

Includes shared base fields for all events, specialized models for
install and purchase events and API response models.
"""
from __future__ import annotations

from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field, field_validator

class BaseEventIn(BaseModel):
    """
        Base schema for all incoming game events.

        Defines common metadata shared by install and purchase events,
        such as player, app, platform and timestamps.
        """
    event_type: Literal["install", "purchase"]
    event_id: str = Field(..., description="Client-generated UUID for idempotency.")
    occurred_at: str = Field(..., description="ISO8601 timestamp (UTC) when the event occurred.")
    player_id: str
    app_id: str
    platform: Literal["ios", "android"]

    session_id: Optional[str] = None
    device_id: Optional[str] = None
    country: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class InstallEventIn(BaseEventIn):
    event_type: Literal["install"] = "install"
    campaign: Optional[str] = None
    ad_group: Optional[str] = None
    creative: Optional[str] = None

class PurchaseEventIn(BaseEventIn):
    """
        Schema for a game purchase event.

        Extends the base event with purchase-specific fields
        including product, quantity, amount and currency.
        """
    event_type: Literal["purchase"] = "purchase"
    product_id: str
    quantity: int = Field(default=1, ge=1)
    amount_micros: int = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)
    transaction_id: Optional[str] = None
    store: Optional[Literal["app_store", "google_play", "other"]] = None

    @field_validator("currency")
    @classmethod
    def upper_currency(cls, v: str) -> str:
        """
        Normalizes currency codes to uppercase ISO format.
        """
        return v.upper()

class EventAccepted(BaseModel):
    """
    API response model returned after successful event ingestion.
    """
    status: Literal["accepted"] = "accepted"
    event_id: str
