from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional
import boto3

@dataclass(frozen=True)
class FirehoseConfig:
    delivery_stream_name: str
    region_name: Optional[str] = None

class FirehoseClient:
    """
       Client responsible for sending event data to AWS Kinesis Firehose.
       Encapsulates Firehose configuration and provides a simple interface
       for serializing events and delivering them to a configured Firehose
       delivery stream.
       """
    def __init__(self, config: FirehoseConfig, boto3_client: Any | None = None):
        self.config = config
        self._client = boto3_client or boto3.client("firehose", region_name=config.region_name)

    def put_event(self, event: Dict[str, Any]) -> None:
        """
        Sends a single event to AWS Kinesis Firehose.
        The event is serialized as a compact JSON payload and written
        to the configured Firehose delivery stream.
        """
        payload = (json.dumps(event, separators=(",", ":")) + "\n").encode("utf-8")
        self._client.put_record(
            DeliveryStreamName=self.config.delivery_stream_name,
            Record={"Data": payload},
        )
