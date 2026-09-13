"""
Real-Time Aviation Aircraft Producer

Pipeline:

ADSB.lol API
    ↓
Python ingestion service
    ↓
Redpanda
    ↓
Topic: aircraft-observations

This producer:

1. Fetches live aircraft data from ADSB.lol.
2. Processes one geographic region per collection cycle.
3. Rotates through all configured regions.
4. Prevents rapid API requests that may trigger rate limits.
5. Handles HTTP 429 rate-limit responses.
6. Handles HTTP 502, 503, and 504 temporary errors.
7. Handles timeout, DNS, and connection errors.
8. Uses retry and exponential backoff logic.
9. Publishes valid aircraft observations to Redpanda.
10. Handles Redpanda connection failures.
11. Continues running when one region fails.
12. Handles graceful shutdown.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

import requests
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka.errors import KafkaError


# ---------------------------------------------------------------------
# Project configuration
# ---------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

load_dotenv(
    os.path.join(
        PROJECT_ROOT,
        ".env"
    )
)


# ---------------------------------------------------------------------
# Application configuration
# ---------------------------------------------------------------------

REDPANDA_BROKER = os.getenv(
    "REDPANDA_BROKER",
    "localhost:9092"
).strip()

# Correct the old incorrect port if it exists in .env.
if REDPANDA_BROKER in {
    "localhost:19092",
    "127.0.0.1:19092"
}:
    REDPANDA_BROKER = REDPANDA_BROKER.replace(
        "19092",
        "9092"
    )


KAFKA_TOPIC = os.getenv(
    "KAFKA_TOPIC",
    "aircraft-observations"
).strip()


ADSB_BASE_URL = os.getenv(
    "ADSB_BASE_URL",
    "https://api.adsb.lol"
).rstrip("/")


# ---------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------

# One region is processed during each cycle.
#
# With five regions and a 60-second interval:
#
# Riyadh  -> cycle 1
# Jeddah  -> cycle 2
# Dammam  -> cycle 3
# Dubai   -> cycle 4
# Doha    -> cycle 5
#
# Each region is therefore requested approximately every 5 minutes.
REGION_POLL_INTERVAL_SECONDS = int(
    os.getenv(
        "REGION_POLL_INTERVAL_SECONDS",
        "60"
    )
)


# Delay before retrying a rate-limited or temporary API request.
INITIAL_API_RETRY_DELAY_SECONDS = int(
    os.getenv(
        "INITIAL_API_RETRY_DELAY_SECONDS",
        "60"
    )
)


MAX_API_RETRIES = int(
    os.getenv(
        "MAX_API_RETRIES",
        "3"
    )
)


REQUEST_TIMEOUT_SECONDS = int(
    os.getenv(
        "REQUEST_TIMEOUT_SECONDS",
        "30"
    )
)


# Do not immediately retry the same region after a failure.
REGION_FAILURE_COOLDOWN_SECONDS = int(
    os.getenv(
        "REGION_FAILURE_COOLDOWN_SECONDS",
        "120"
    )
)


# ---------------------------------------------------------------------
# Redpanda configuration
# ---------------------------------------------------------------------

MAX_KAFKA_CONNECTION_RETRIES = int(
    os.getenv(
        "MAX_KAFKA_CONNECTION_RETRIES",
        "10"
    )
)


KAFKA_CONNECTION_RETRY_DELAY_SECONDS = int(
    os.getenv(
        "KAFKA_CONNECTION_RETRY_DELAY_SECONDS",
        "10"
    )
)


KAFKA_REQUEST_TIMEOUT_MS = int(
    os.getenv(
        "KAFKA_REQUEST_TIMEOUT_MS",
        "30000"
    )
)


KAFKA_DELIVERY_TIMEOUT_MS = int(
    os.getenv(
        "KAFKA_DELIVERY_TIMEOUT_MS",
        "120000"
    )
)


# ---------------------------------------------------------------------
# Regional configuration
# ---------------------------------------------------------------------

REGIONS: dict[str, dict[str, Any]] = {
    "riyadh": {
        "latitude": 24.7136,
        "longitude": 46.6753,
        "distance": 250,
    },
    "jeddah": {
        "latitude": 21.4858,
        "longitude": 39.1925,
        "distance": 250,
    },
    "dammam": {
        "latitude": 26.4207,
        "longitude": 50.0888,
        "distance": 250,
    },
    "dubai": {
        "latitude": 25.2048,
        "longitude": 55.2708,
        "distance": 250,
    },
    "doha": {
        "latitude": 25.2854,
        "longitude": 51.5310,
        "distance": 250,
    },
}


# ---------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(
    "aircraft_producer"
)


# ---------------------------------------------------------------------
# HTTP session
# ---------------------------------------------------------------------

HTTP_SESSION = requests.Session()

HTTP_SESSION.headers.update(
    {
        "User-Agent": (
            "real-time-flight-analytics-project/1.0 "
            "(educational data analytics project)"
        ),
        "Accept": "application/json",
    }
)


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def clean_text(
    value: Any
) -> str | None:
    """
    Return cleaned text.

    Empty values and common null-like values become None.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if text.lower() in {
        "none",
        "null",
        "nan",
        "unknown",
    }:
        return None

    return text


def clean_number(
    value: Any
) -> float | int | None:
    """
    Convert a value into an integer or float.

    Invalid values become None.
    Boolean values are rejected.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    try:
        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except (
        TypeError,
        ValueError
    ):
        return None


def clean_callsign(
    value: Any
) -> str | None:
    """
    Clean an aircraft callsign.

    ADSB.lol may return callsigns with trailing spaces.
    """

    callsign = clean_text(
        value
    )

    if callsign is None:
        return None

    return callsign.strip()


def build_api_url(
    region: dict[str, Any]
) -> str:
    """
    Build the ADSB.lol regional aircraft endpoint.
    """

    return (
        f"{ADSB_BASE_URL}/v2/lat/"
        f"{region['latitude']}/lon/"
        f"{region['longitude']}/dist/"
        f"{region['distance']}"
    )


def get_retry_after_seconds(
    response: requests.Response
) -> int | None:
    """
    Read the Retry-After response header.

    Returns None when the header is missing or invalid.
    """

    retry_after_header = response.headers.get(
        "Retry-After"
    )

    if not retry_after_header:
        return None

    try:
        retry_after = int(
            retry_after_header
        )

        return max(
            retry_after,
            INITIAL_API_RETRY_DELAY_SECONDS
        )

    except ValueError:
        return None


def calculate_retry_delay(
    attempt: int,
    retry_after: int | None = None
) -> int:
    """
    Calculate retry delay using Retry-After or exponential backoff.
    """

    if retry_after is not None:
        return retry_after

    return (
        INITIAL_API_RETRY_DELAY_SECONDS
        * (2 ** (attempt - 1))
    )


# ---------------------------------------------------------------------
# ADSB.lol API functions
# ---------------------------------------------------------------------

def fetch_aircraft_snapshot(
    region_code: str,
    region: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Fetch live aircraft data for one region.

    Handles:

    - HTTP 200
    - HTTP 429
    - HTTP 502
    - HTTP 503
    - HTTP 504
    - Timeout errors
    - Connection errors
    - DNS errors
    - Invalid JSON responses
    - Unexpected API response formats
    """

    url = build_api_url(
        region
    )

    logger.info(
        "Fetching live aircraft data for %s (%s)",
        region_code.title(),
        region_code
    )

    logger.info(
        "Fetching aircraft data from: %s",
        url
    )

    retryable_status_codes = {
        429,
        502,
        503,
        504,
    }

    for attempt in range(
        1,
        MAX_API_RETRIES + 1
    ):

        try:
            response = HTTP_SESSION.get(
                url,
                timeout=REQUEST_TIMEOUT_SECONDS
            )

            status_code = response.status_code

            # ---------------------------------------------------------
            # Successful response
            # ---------------------------------------------------------

            if status_code == 200:

                try:
                    payload = response.json()

                except ValueError as error:

                    logger.warning(
                        "Invalid JSON response for %s: %s",
                        region_code,
                        error
                    )

                    return []

                if not isinstance(
                    payload,
                    dict
                ):

                    logger.warning(
                        "Unexpected response format for region %s",
                        region_code
                    )

                    return []

                aircraft = payload.get(
                    "ac",
                    payload.get(
                        "aircraft",
                        []
                    )
                )

                if not isinstance(
                    aircraft,
                    list
                ):

                    logger.warning(
                        "Unexpected aircraft field for region %s",
                        region_code
                    )

                    return []

                logger.info(
                    "Successfully fetched aircraft snapshot: %s aircraft",
                    len(aircraft)
                )

                return aircraft

            # ---------------------------------------------------------
            # Rate limit and temporary server errors
            # ---------------------------------------------------------

            if status_code in retryable_status_codes:

                retry_after = get_retry_after_seconds(
                    response
                )

                retry_delay = calculate_retry_delay(
                    attempt=attempt,
                    retry_after=retry_after
                )

                logger.warning(
                    (
                        "ADSB.lol returned HTTP %s for %s. "
                        "Waiting %s seconds before retry %s/%s."
                    ),
                    status_code,
                    region_code,
                    retry_delay,
                    attempt,
                    MAX_API_RETRIES
                )

                if attempt < MAX_API_RETRIES:

                    time.sleep(
                        retry_delay
                    )

                    continue

                logger.error(
                    (
                        "Retries exhausted for region %s "
                        "after HTTP %s."
                    ),
                    region_code,
                    status_code
                )

                return []

            # ---------------------------------------------------------
            # Other HTTP errors
            # ---------------------------------------------------------

            logger.warning(
                (
                    "ADSB.lol returned non-retryable HTTP %s "
                    "for region %s."
                ),
                status_code,
                region_code
            )

            return []

        except requests.exceptions.Timeout as error:

            retry_delay = calculate_retry_delay(
                attempt=attempt
            )

            logger.warning(
                (
                    "Request timeout for %s: %s. "
                    "Waiting %s seconds before retry %s/%s."
                ),
                region_code,
                error,
                retry_delay,
                attempt,
                MAX_API_RETRIES
            )

            if attempt < MAX_API_RETRIES:

                time.sleep(
                    retry_delay
                )

                continue

            logger.error(
                "Request timeout retries exhausted for %s",
                region_code
            )

            return []

        except requests.exceptions.ConnectionError as error:

            retry_delay = calculate_retry_delay(
                attempt=attempt
            )

            logger.warning(
                (
                    "Connection or DNS error for %s: %s. "
                    "Waiting %s seconds before retry %s/%s."
                ),
                region_code,
                error,
                retry_delay,
                attempt,
                MAX_API_RETRIES
            )

            if attempt < MAX_API_RETRIES:

                time.sleep(
                    retry_delay
                )

                continue

            logger.error(
                "Connection retries exhausted for %s",
                region_code
            )

            return []

        except requests.exceptions.RequestException as error:

            logger.warning(
                "ADSB.lol request failed for %s: %s",
                region_code,
                error
            )

            return []

        except Exception:

            logger.exception(
                "Unexpected API error for region %s",
                region_code
            )

            return []

    return []


# ---------------------------------------------------------------------
# Observation transformation
# ---------------------------------------------------------------------

def create_observation(
    aircraft: dict[str, Any],
    region_code: str,
    snapshot_observed_at: str
) -> dict[str, Any] | None:
    """
    Convert one ADSB.lol aircraft record into a Redpanda observation.
    """

    aircraft_hex = clean_text(
        aircraft.get(
            "hex"
        )
    )

    if aircraft_hex is None:

        logger.debug(
            "Skipping aircraft without hexadecimal identifier"
        )

        return None

    aircraft_hex = aircraft_hex.lower()

    latitude = clean_number(
        aircraft.get(
            "lat"
        )
    )

    longitude = clean_number(
        aircraft.get(
            "lon"
        )
    )

    if latitude is None or longitude is None:

        logger.debug(
            (
                "Skipping aircraft %s because latitude "
                "or longitude is missing"
            ),
            aircraft_hex
        )

        return None

    observation = {
        "event_type": "AIRCRAFT_OBSERVATION",

        "aircraft_hex": aircraft_hex,

        "callsign": clean_callsign(
            aircraft.get(
                "flight"
            )
        ),

        "registration": clean_text(
            aircraft.get(
                "r"
            )
        ),

        "aircraft_type": clean_text(
            aircraft.get(
                "t"
            )
        ),

        "latitude": latitude,

        "longitude": longitude,

        "altitude_baro": clean_number(
            aircraft.get(
                "alt_baro"
            )
        ),

        "altitude_geometric": clean_number(
            aircraft.get(
                "alt_geom"
            )
        ),

        "ground_speed": clean_number(
            aircraft.get(
                "gs"
            )
        ),

        "track": clean_number(
            aircraft.get(
                "track"
            )
        ),

        "vertical_rate": clean_number(
            aircraft.get(
                "baro_rate"
            )
        ),

        "squawk": clean_text(
            aircraft.get(
                "squawk"
            )
        ),

        "category": clean_text(
            aircraft.get(
                "category"
            )
        ),

        "emergency_status": clean_text(
            aircraft.get(
                "emergency"
            )
        ),

        "region_code": region_code,

        "source": "ADSB.lol",

        "observed_at": snapshot_observed_at,
    }

    return observation


# ---------------------------------------------------------------------
# Redpanda producer
# ---------------------------------------------------------------------

def create_kafka_producer() -> KafkaProducer:
    """
    Create and return a Kafka-compatible Redpanda producer.
    """

    logger.info(
        "Connecting to Redpanda at %s",
        REDPANDA_BROKER
    )

    logger.info(
        "Redpanda topic: %s",
        KAFKA_TOPIC
    )

    for attempt in range(
        1,
        MAX_KAFKA_CONNECTION_RETRIES + 1
    ):

        try:

            producer = KafkaProducer(

                bootstrap_servers=[
                    REDPANDA_BROKER
                ],

                value_serializer=lambda value: json.dumps(
                    value,
                    separators=(
                        ",",
                        ":"
                    )
                ).encode(
                    "utf-8"
                ),

                key_serializer=lambda value: value.encode(
                    "utf-8"
                ),

                acks="all",

                retries=5,

                request_timeout_ms=KAFKA_REQUEST_TIMEOUT_MS,

                delivery_timeout_ms=KAFKA_DELIVERY_TIMEOUT_MS,

                linger_ms=100,

                batch_size=16384,
            )

            logger.info(
                "Successfully connected to Redpanda at %s",
                REDPANDA_BROKER
            )

            return producer

        except KafkaError as error:

            logger.warning(
                (
                    "Redpanda connection attempt %s/%s failed: %s"
                ),
                attempt,
                MAX_KAFKA_CONNECTION_RETRIES,
                error
            )

            if attempt >= MAX_KAFKA_CONNECTION_RETRIES:

                logger.error(
                    (
                        "Unable to connect to Redpanda after %s attempts"
                    ),
                    MAX_KAFKA_CONNECTION_RETRIES
                )

                raise

            logger.info(
                (
                    "Waiting %s seconds before reconnecting "
                    "to Redpanda..."
                ),
                KAFKA_CONNECTION_RETRY_DELAY_SECONDS
            )

            time.sleep(
                KAFKA_CONNECTION_RETRY_DELAY_SECONDS
            )

        except Exception:

            logger.exception(
                "Unexpected error while creating Redpanda producer"
            )

            if attempt >= MAX_KAFKA_CONNECTION_RETRIES:

                raise

            time.sleep(
                KAFKA_CONNECTION_RETRY_DELAY_SECONDS
            )

    raise RuntimeError(
        "Could not create Redpanda producer"
    )


def publish_observation(
    producer: KafkaProducer,
    observation: dict[str, Any]
) -> None:
    """
    Publish one aircraft observation to Redpanda.
    """

    aircraft_hex = observation[
        "aircraft_hex"
    ]

    future = producer.send(
        KAFKA_TOPIC,
        key=aircraft_hex,
        value=observation
    )

    record_metadata = future.get(
        timeout=30
    )

    logger.debug(
        (
            "Published aircraft %s to topic %s, "
            "partition %s, offset %s"
        ),
        aircraft_hex,
        record_metadata.topic,
        record_metadata.partition,
        record_metadata.offset
    )


# ---------------------------------------------------------------------
# Region processing
# ---------------------------------------------------------------------

def process_region(
    producer: KafkaProducer,
    region_code: str,
    region: dict[str, Any]
) -> int:
    """
    Fetch one region and publish its aircraft observations.

    Duplicate aircraft hexadecimal identifiers in the same snapshot
    are published only once.
    """

    snapshot_observed_at = datetime.now(
        timezone.utc
    ).isoformat()

    aircraft_records = fetch_aircraft_snapshot(
        region_code=region_code,
        region=region
    )

    published_count = 0

    skipped_count = 0

    duplicate_count = 0

    seen_aircraft: set[str] = set()

    for aircraft in aircraft_records:

        if not isinstance(
            aircraft,
            dict
        ):

            skipped_count += 1

            continue

        aircraft_hex = clean_text(
            aircraft.get(
                "hex"
            )
        )

        if aircraft_hex is None:

            skipped_count += 1

            continue

        aircraft_hex = aircraft_hex.lower()

        if aircraft_hex in seen_aircraft:

            duplicate_count += 1

            continue

        seen_aircraft.add(
            aircraft_hex
        )

        observation = create_observation(
            aircraft=aircraft,
            region_code=region_code,
            snapshot_observed_at=snapshot_observed_at
        )

        if observation is None:

            skipped_count += 1

            continue

        try:

            publish_observation(
                producer=producer,
                observation=observation
            )

            published_count += 1

        except KafkaError as error:

            logger.error(
                "Failed to publish aircraft %s: %s",
                observation["aircraft_hex"],
                error
            )

        except Exception:

            logger.exception(
                (
                    "Unexpected publishing error for aircraft %s"
                ),
                observation["aircraft_hex"]
            )

    try:

        producer.flush(
            timeout=30
        )

    except Exception:

        logger.exception(
            (
                "Failed to flush producer after region %s"
            ),
            region_code
        )

    logger.info(
        (
            "Published region '%s': "
            "received=%s, published=%s, skipped=%s, duplicates=%s"
        ),
        region_code,
        len(aircraft_records),
        published_count,
        skipped_count,
        duplicate_count
    )

    return published_count


# ---------------------------------------------------------------------
# Collection cycle
# ---------------------------------------------------------------------

def run_region_cycle(
    producer: KafkaProducer,
    region_code: str,
    region: dict[str, Any]
) -> int:
    """
    Run one collection cycle for one region.
    """

    cycle_started_at = time.monotonic()

    total_published = 0

    try:

        total_published = process_region(
            producer=producer,
            region_code=region_code,
            region=region
        )

    except Exception:

        logger.exception(
            (
                "Unexpected error while processing region %s"
            ),
            region_code
        )

    cycle_duration = (
        time.monotonic()
        - cycle_started_at
    )

    logger.info(
        (
            "Region cycle completed for %s. "
            "Published observations: %s"
        ),
        region_code,
        total_published
    )

    logger.info(
        "Region cycle duration: %.2f seconds",
        cycle_duration
    )

    return total_published


# ---------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------

def main() -> None:
    """
    Start the continuous aircraft producer.

    Only one region is requested during each cycle.
    This significantly reduces ADSB.lol rate-limit problems.
    """

    logger.info(
        "Starting ADSB.lol to Redpanda producer"
    )

    logger.info(
        "Redpanda broker: %s",
        REDPANDA_BROKER
    )

    logger.info(
        "Kafka topic: %s",
        KAFKA_TOPIC
    )

    logger.info(
        "Configured regions: %s",
        ", ".join(
            REGIONS.keys()
        )
    )

    logger.info(
        "Region polling interval: %s seconds",
        REGION_POLL_INTERVAL_SECONDS
    )

    producer: KafkaProducer | None = None

    region_items = list(
        REGIONS.items()
    )

    region_index = 0

    try:

        producer = create_kafka_producer()

        while True:

            region_code, region = region_items[
                region_index
            ]

            logger.info(
                (
                    "Starting collection cycle for region %s "
                    "(%s/%s)"
                ),
                region_code,
                region_index + 1,
                len(region_items)
            )

            run_region_cycle(
                producer=producer,
                region_code=region_code,
                region=region
            )

            region_index = (
                region_index + 1
            ) % len(region_items)

            logger.info(
                (
                    "Waiting %s seconds before the next "
                    "regional API request..."
                ),
                REGION_POLL_INTERVAL_SECONDS
            )

            time.sleep(
                REGION_POLL_INTERVAL_SECONDS
            )

    except KeyboardInterrupt:

        logger.info(
            "Producer stopped by user"
        )

    except Exception:

        logger.exception(
            "Producer stopped because of an unexpected error"
        )

        sys.exit(1)

    finally:

        if producer is not None:

            try:

                producer.flush(
                    timeout=30
                )

            except Exception:

                logger.exception(
                    "Error while flushing Redpanda producer"
                )

            try:

                producer.close(
                    timeout=30
                )

            except Exception:

                logger.exception(
                    "Error while closing Redpanda producer"
                )

        HTTP_SESSION.close()

        logger.info(
            "Producer shutdown completed"
        )


# ---------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()