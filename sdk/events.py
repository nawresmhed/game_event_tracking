"""
Event definitions used by the SDK for sending game events.

Defines common event fields and concrete event types for installs
and purchases, including helpers for event creation and serialization.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class BaseEvent:
    """Common event envelope."""
    event_type: str
    event_id: str
    occurred_at: str
    player_id: str
    app_id: str
    platform: str  # "ios" | "android"
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    country: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}

@dataclass(frozen=True)
class InstallEvent(BaseEvent):
    campaign: Optional[str] = None
    ad_group: Optional[str] = None
    creative: Optional[str] = None

    @staticmethod
    def create(
        *,
        player_id: str,
        app_id: str,
        platform: str,
        occurred_at: Optional[str] = None,
        event_id: Optional[str] = None,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        country: Optional[str] = None,
        campaign: Optional[str] = None,
        ad_group: Optional[str] = None,
        creative: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> "InstallEvent":
        """
            Event representing a game installation.

            Includes optional attribution fields such as campaign
            and advertising metadata.
        """
        return InstallEvent(
            event_type="install",
            event_id=event_id or str(uuid.uuid4()),
            occurred_at=occurred_at or _utc_now_iso(),
            player_id=player_id,
            app_id=app_id,
            platform=platform,
            session_id=session_id,
            device_id=device_id,
            country=country,
            properties=properties,
            campaign=campaign,
            ad_group=ad_group,
            creative=creative,
        )

@dataclass(frozen=True)
class PurchaseEvent(BaseEvent):
    """
    Event representing an in-game purchase.
    Includes product, pricing, and transaction information.
    """
    product_id: str = ""
    quantity: int = 1
    amount_micros: int = 0
    currency: str = "USD"
    transaction_id: Optional[str] = None
    store: Optional[str] = None

    @staticmethod
    def create(
        *,
        player_id: str,
        app_id: str,
        platform: str,
        product_id: str,
        amount_micros: int,
        currency: str,
        quantity: int = 1,
        occurred_at: Optional[str] = None,
        event_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        store: Optional[str] = None,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        country: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> "PurchaseEvent":
        return PurchaseEvent(
            event_type="purchase",
            event_id=event_id or str(uuid.uuid4()),
            occurred_at=occurred_at or _utc_now_iso(),
            player_id=player_id,
            app_id=app_id,
            platform=platform,
            session_id=session_id,
            device_id=device_id,
            country=country,
            properties=properties,
            product_id=product_id,
            quantity=quantity,
            amount_micros=amount_micros,
            currency=currency.upper(),
            transaction_id=transaction_id,
            store=store,
        )
