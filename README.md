# Game Event Tracking – SDK & Ingestion API

## Project Overview

This project implements a **basic event tracking system** for a mobile game studio.
It demonstrates how game clients can send **install** and **purchase** events to a backend ingestion API, which validates, authenticates deduplicates, and forwards events to a streaming system (AWS Kinesis Firehose).


All external services (AWS, Snowflake) are **mockable**, allowing the project to run locally without cloud infrastructure.

---

## Architecture Overview


 Game Client (SDK)

        |

        |  HTTP POST (JSON + Bearer Auth)

        v

FastAPI Ingestion API

        |

        |  (mocked )

        v

AWS Kinesis Firehose


        |

        v
Snowflake (described, not implemented)


---

## Project Structure

game_event_tracking_simple/

├── api/

│   ├── __init__.py

│   ├── main.py              # FastAPI app & endpoints

│   ├── models.py            #  request/response models

│   └── firehose_client.py   # Firehose abstraction (boto3)

│
├── sdk/

│   ├── __init__.py

│   ├── client.py            # SDK HTTP client (auth, retries)

│   └── events.py            # Event models (install, purchase)

│
├── tests/

│   ├── test_api.py

│   └── test_sdk.py

│
├── send_events.py           # Example script simulating a game client

├── .env                     # Environment configuration

├── requirements.txt

└── README.md

---
## Project Components
### API Layer (`api/`)

**`api/main.py`**  
Defines the FastAPI application and REST endpoints for ingesting game events.  
Responsible for:
- Loading environment configuration
- Authenticating requests using Bearer tokens
- Validating install and purchase event schemas
- Deduplicating events using event IDs
- Forwarding events to AWS Kinesis Firehose (or a mock implementation)
- Exposing health and ingestion endpoints

**`api/models.py`**  
Contains Pydantic models defining the schema for incoming install and purchase events.  
Ensures strong validation, type safety, and consistent data contracts between clients and the API.

**`api/firehose_client.py`**  
Implements an abstraction layer for sending events to AWS Kinesis Firehose using boto3.  
Encapsulates Firehose configuration and isolates AWS-specific logic from the API.

---

### SDK Layer (`sdk/`)

**`sdk/client.py`**  
Implements the Python SDK used by game clients to send events to the ingestion API.  
Handles:
- HTTP communication
- Automatic Bearer token authorization
- Retry and timeout logic
- Request payload construction

**`sdk/events.py`**  
Defines event classes (`InstallEvent`, `PurchaseEvent`) used by the SDK.  
Responsible for:
- Event creation
- Timestamp generation
- Unique event ID generation
- Serialization of events to JSON format

---

### Tests (`tests/`)

**`tests/test_api.py`**  
Unit tests for the FastAPI application.  
Uses FastAPI’s `TestClient` to verify basic API behavior while mocking external dependencies such as AWS Firehose.

**`tests/test_sdk.py`**  
Unit tests for the SDK client.  
Verifies correct payload construction, endpoint usage, and authorization headers without making real HTTP requests.

---

### Root-Level Files

**`send_events.py`**  
Example script that simulates a real game client using the SDK.  
Demonstrates how install and purchase events are created and sent to the ingestion API with automatic authorization.

**`.env`**  
Environment configuration file containing API keys, AWS region, Firehose stream name and mock settings.  
Allows behavior to be changed without modifying code.

**`requirements.txt`**  
Lists all Python dependencies required to run the API, SDK and tests.



## How to Use the SDK
The SDK simulates how a real mobile game client would send events to the backend.
### Create a client

```python
from sdk import GameEventClient, GameEventClientConfig

client = GameEventClient(
    GameEventClientConfig(
        base_url="http://127.0.0.1:8000",
        api_key="dev-secret"
    )
)
```

### Send an install event

```python
from sdk import InstallEvent

install_event = InstallEvent.create(
    player_id="player_1",
    app_id="com.game.test",
    platform="ios"
)

client.send_install(install_event)
```

### Send a purchase event

```python
from sdk import PurchaseEvent

purchase_event = PurchaseEvent.create(
    player_id="player_1",
    app_id="com.game.test",
    platform="ios",
    product_id="gems_pack_01",
    quantity=1,
    amount_micros=4_990_000,
    currency="EUR"
)

client.send_purchase(purchase_event)
```
### Running the Project
Create virtual environment
```python
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate # macOS/Linux

```
Install dependencies
```python
pip install -r requirements.txt


```
Start the API
```python
uvicorn api.main:app --reload --port 8000
```
Verify:

http://127.0.0.1:8000/health

http://127.0.0.1:8000/docs

Send events using the SDK
```python
python send_events.py

```
Expected output
```python
Install response: 200 {"status":"accepted","event_id":"..."}
Purchase response: 200 {"status":"accepted","event_id":"..."}
```

Run tests
From project root:
```python
pytest -q

```
---
## Snowflake Design (Conceptual)
```sql
CREATE TABLE game_events (
    event_id STRING,
    event_type STRING,
    occurred_at TIMESTAMP,
    received_at TIMESTAMP,
    player_id STRING,
    app_id STRING,
    platform STRING,
    product_id STRING,
    quantity INTEGER,
    amount_micros NUMBER,
    currency STRING,
    raw_payload VARIANT
);
```

## Design Decisions

- Separation between SDK and API: The SDK only creates and sends events, while the API is responsible for validation, authentication and forwarding. This mirrors real-world client → backend architectures.
- Bearer token authentication
- Strong schema validation
- Mockable AWS Firehose integration
- Monetary values stored in micros to avoid floating-point issues

---

## Assumptions Made

- Client-generated event IDs are unique
- Moderate event volume
- Snowflake ingestion is handled via Firehose
- Currency conversion handled in analytics layer

---

## What Would Be Done Next

- Add monitoring and logging : 
  - Log all requests and failures in a structured format 
  - track basic metrics such as request volume, error rate, and delivery latency.
  - Add alerts for abnormal behavior.
- Data quality checks : Validate critical fields (player_id, timestamps, amount, currency)
- Snowflake optimization (partitioning, clustering): 
  - Partition data by event_date ( occurred_at).
  - Cluster by event_type, app_id
- Optimize the Snowflake pipeline: 

  - Store raw events first, then transform them into analytics tables.

  - Add schema versioning so events can evolve without breaking queries.

  - Normalize currencies and enrich events in downstream transformations

---

