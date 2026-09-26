"""
Real-Time Flight Operations & Aviation Analytics
Aircraft Stream Processor

Consumes aircraft observations from Redpanda and generates
derived aviation events in PostgreSQL.

Input topic:
    aircraft-observations

Output table:
    aviation.fact_aviation_event
"""

import json
import logging
import os
import signal
import time
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import psycopg2
from psycopg2.extras import Json, RealDictCursor
from confluent_kafka import Consumer, KafkaException

from ingestion.postgres_loader import (
    get_region_id,
    upsert_aircraft_dimension,
    insert_aircraft_position,
)


# ---------------------------------------------------------------------
# Project root
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
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("aircraft-stream-processor")


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

KAFKA_BROKER = os.getenv(
    "REDPANDA_BROKER",
    "localhost:9092",
)

KAFKA_TOPIC = os.getenv(
    "KAFKA_TOPIC",
    "aircraft-observations",
)

KAFKA_GROUP_ID = os.getenv(
    "PROCESSOR_GROUP_ID",
    "aircraft-stream-processor-v1",
)

POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost",
)

POSTGRES_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5433",
    )
)

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "flight_analytics",
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "flight_analytics",
)

POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "change_me",
)


# ---------------------------------------------------------------------
# Processing thresholds
# ---------------------------------------------------------------------

# An altitude difference greater than this creates an event.
ALTITUDE_CHANGE_THRESHOLD = 3000

# A speed difference greater than this creates an event.
SPEED_CHANGE_THRESHOLD = 80

# A vertical rate greater than this creates an event.
VERTICAL_RATE_THRESHOLD = 1500

# Prevent repeated events for the same aircraft and event type
# during this cooldown period.
EVENT_COOLDOWN_SECONDS = 300


# ---------------------------------------------------------------------
# Runtime state
# ---------------------------------------------------------------------

running = True

# Stores the previous observation for each aircraft.
previous_aircraft_state: Dict[str, Dict[str, Any]] = {}

# Stores the latest time an event was generated for an aircraft/event type.
last_event_time: Dict[str, float] = {}

# Tracks the pipeline run currently being processed.
current_run_id: Optional[str] = None


# ---------------------------------------------------------------------
# Signal handling
# ---------------------------------------------------------------------

def handle_shutdown(signum, frame):
    """
    Gracefully stop the processor when Ctrl+C is pressed.
    """
    global running

    logger.info(
        "Shutdown signal received. Stopping processor..."
    )

    running = False


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def parse_observed_at(
    value: Optional[str],
) -> datetime:
    """
    Convert an ISO timestamp into a timezone-aware datetime.

    Example:
        2026-09-13T17:57:42.293568+00:00
    """

    if not value:
        return datetime.now(timezone.utc)

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except ValueError:
        logger.warning(
            "Invalid observed_at value '%s'. "
            "Using current UTC time.",
            value,
        )

        return datetime.now(timezone.utc)


def safe_float(
    value: Any,
) -> Optional[float]:
    """
    Convert a value to float when possible.
    """

    if value is None:
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def safe_int(
    value: Any,
) -> Optional[int]:
    """
    Convert a value to integer when possible.
    """

    if value is None:
        return None

    try:
        return int(value)

    except (TypeError, ValueError):
        return None


def get_aircraft_hex(
    observation: Dict[str, Any],
) -> Optional[str]:
    """
    Extract the aircraft identifier.
    """

    aircraft_hex = observation.get(
        "aircraft_hex"
    )

    if not aircraft_hex:
        return None

    return str(aircraft_hex).strip().lower()


def event_is_on_cooldown(
    aircraft_hex: str,
    event_type: str,
) -> bool:
    """
    Check whether the same event was recently generated.
    """

    key = f"{aircraft_hex}:{event_type}"

    previous_time = last_event_time.get(key)

    if previous_time is None:
        return False

    elapsed = time.time() - previous_time

    return elapsed < EVENT_COOLDOWN_SECONDS


def mark_event_created(
    aircraft_hex: str,
    event_type: str,
) -> None:
    """
    Record the event creation time.
    """

    key = f"{aircraft_hex}:{event_type}"

    last_event_time[key] = time.time()


# ---------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------

def create_postgres_connection():
    """
    Create a PostgreSQL connection.
    """

    logger.info(
        "Connecting to PostgreSQL at %s:%s...",
        POSTGRES_HOST,
        POSTGRES_PORT,
    )

    connection = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )

    connection.autocommit = True

    logger.info(
        "PostgreSQL connection successful."
    )

    return connection


def insert_event(
    connection,
    event_time: datetime,
    event_type: str,
    aircraft_hex: Optional[str],
    region_code: Optional[str],
    event_value: Optional[float],
    event_description: str,
    source: str,
    event_payload: Dict[str, Any],
    run_id: str,
) -> None:
    """
    Insert a derived event into aviation.fact_aviation_event.
    """

    sql = """
        INSERT INTO aviation.fact_aviation_event (
            event_time,
            event_type,
            aircraft_hex,
            region_code,
            event_value,
            event_description,
            source,
            event_payload,
            run_id
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(
            sql,
            (
                event_time,
                event_type,
                aircraft_hex,
                region_code,
                event_value,
                event_description,
                source,
                Json(event_payload),
                run_id,
            ),
        )

    logger.info(
        "Generated event: run_id=%s type=%s aircraft=%s region=%s value=%s",
        run_id,
        event_type,
        aircraft_hex,
        region_code,
        event_value,
    )


# ---------------------------------------------------------------------
# Live aircraft position persistence
# ---------------------------------------------------------------------

def build_loader_aircraft(
    observation: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert the normalized Kafka observation into the field structure
    expected by ingestion.postgres_loader.
    """

    return {
        "hex": observation.get("aircraft_hex"),
        "flight": observation.get("callsign"),
        "t": observation.get("aircraft_type"),
        "r": observation.get("registration"),
        "lat": observation.get("latitude"),
        "lon": observation.get("longitude"),
        "alt_baro": observation.get("altitude_baro"),
        "alt_geom": observation.get("altitude_geom"),
        "gs": observation.get("ground_speed"),
        "track": observation.get("track"),
        "baro_rate": observation.get("vertical_rate"),
        "squawk": observation.get("squawk"),
        "category": observation.get("category"),
        "emergency": observation.get("emergency_status"),
        "source": observation.get(
            "source",
            "adsb.lol",
        ),
    }


def persist_aircraft_position(
    connection,
    observation: Dict[str, Any],
    observed_at: datetime,
    region_code: Optional[str],
    run_id: str,
) -> bool:
    """
    Persist one live aircraft observation into the aircraft dimension
    and position fact table.
    """

    aircraft_hex = get_aircraft_hex(
        observation
    )

    if not aircraft_hex:
        logger.warning(
            "Skipping position persistence without aircraft_hex."
        )
        return False

    if not region_code:
        logger.warning(
            "Skipping position persistence for aircraft %s "
            "because region_code is missing.",
            aircraft_hex,
        )
        return False

    latitude = safe_float(
        observation.get("latitude")
    )

    longitude = safe_float(
        observation.get("longitude")
    )

    if latitude is None or longitude is None:
        logger.debug(
            "Skipping position persistence for aircraft %s "
            "because latitude or longitude is missing.",
            aircraft_hex,
        )
        return False

    loader_aircraft = build_loader_aircraft(
        observation
    )

    try:
        # Use RealDictCursor consistently with the PostgreSQL loader.
        # This guarantees RETURNING results can be accessed by column name.
        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:

            region_id = get_region_id(
                cursor=cursor,
                region_code=region_code,
            )

            aircraft_id = upsert_aircraft_dimension(
                cursor=cursor,
                aircraft=loader_aircraft,
                observed_at=observed_at,
            )

            if aircraft_id is None:
                logger.warning(
                    "Aircraft dimension upsert returned no ID for %s.",
                    aircraft_hex,
                )
                return False

            inserted = insert_aircraft_position(
                cursor=cursor,
                aircraft=loader_aircraft,
                aircraft_id=aircraft_id,
                region_id=region_id,
                region_code=region_code,
                snapshot={
                    "source": observation.get(
                        "source",
                        "adsb.lol",
                    ),
                },
                observed_at=observed_at,
                run_id=run_id,
            )

        return inserted

    except Exception:
        logger.exception(
            "Failed to persist live position for aircraft %s.",
            aircraft_hex,
        )
        return False


# ---------------------------------------------------------------------
# Event detection
# ---------------------------------------------------------------------

def process_observation(
    connection,
    observation: Dict[str, Any],
) -> None:
    """
    Process one aircraft observation and generate derived events.
    """

    global current_run_id

    run_id = observation.get("run_id")

    if not run_id:
        logger.warning(
            "Skipping observation without run_id."
        )
        return

    run_id = str(run_id).strip()

    if not run_id:
        logger.warning(
            "Skipping observation with empty run_id."
        )
        return

    if current_run_id != run_id:
        if current_run_id is not None:
            logger.info(
                "New pipeline run detected: %s -> %s. "
                "Clearing in-memory aircraft state.",
                current_run_id,
                run_id,
            )
        else:
            logger.info(
                "Starting processing for pipeline run: %s",
                run_id,
            )

        current_run_id = run_id
        previous_aircraft_state.clear()
        last_event_time.clear()

    aircraft_hex = get_aircraft_hex(
        observation
    )

    if not aircraft_hex:
        logger.warning(
            "Skipping observation without aircraft_hex."
        )
        return

    observed_at = parse_observed_at(
        observation.get("observed_at")
    )

    region_code = observation.get(
        "region_code"
    )

    if region_code:
        region_code = str(
            region_code
        ).strip().lower()

    current_altitude = safe_float(
        observation.get("altitude_baro")
    )

    current_speed = safe_float(
        observation.get("ground_speed")
    )

    current_vertical_rate = safe_float(
        observation.get("vertical_rate")
    )

    current_latitude = safe_float(
        observation.get("latitude")
    )

    current_longitude = safe_float(
        observation.get("longitude")
    )

    current_track = safe_float(
        observation.get("track")
    )

    # Persist every valid live position before calculating derived
    # events. This keeps fact_aircraft_position synchronized with
    # the Redpanda stream.
    persist_aircraft_position(
        connection=connection,
        observation=observation,
        observed_at=observed_at,
        region_code=region_code,
        run_id=run_id,
    )

    current_state = {
        "run_id": run_id,
        "observed_at": observed_at.isoformat(),
        "region_code": region_code,
        "altitude_baro": current_altitude,
        "ground_speed": current_speed,
        "vertical_rate": current_vertical_rate,
        "latitude": current_latitude,
        "longitude": current_longitude,
        "track": current_track,
        "callsign": observation.get(
            "callsign"
        ),
        "registration": observation.get(
            "registration"
        ),
        "aircraft_type": observation.get(
            "aircraft_type"
        ),
    }

    previous_state = previous_aircraft_state.get(
        aircraft_hex
    )

    # First observation for this aircraft.
    if previous_state is None:
        previous_aircraft_state[
            aircraft_hex
        ] = current_state

        logger.info(
            "Registered first observation for aircraft %s.",
            aircraft_hex,
        )

        return

    previous_altitude = safe_float(
        previous_state.get(
            "altitude_baro"
        )
    )

    previous_speed = safe_float(
        previous_state.get(
            "ground_speed"
        )
    )

    previous_region = previous_state.get(
        "region_code"
    )

    # -------------------------------------------------------------
    # Region change event
    # -------------------------------------------------------------

    if (
        previous_region
        and region_code
        and previous_region != region_code
    ):
        event_type = "REGION_CHANGE"

        if not event_is_on_cooldown(
            aircraft_hex,
            event_type,
        ):
            insert_event(
                connection=connection,
                event_time=observed_at,
                event_type=event_type,
                aircraft_hex=aircraft_hex,
                region_code=region_code,
                event_value=None,
                event_description=(
                    f"Aircraft moved from region "
                    f"{previous_region} to {region_code}."
                ),
                source="aircraft_stream_processor",
                event_payload={
                    "previous_region": previous_region,
                    "current_region": region_code,
                    "observation": observation,
                },
                run_id=run_id,
        )

            mark_event_created(
                aircraft_hex,
                event_type,
            )

    # -------------------------------------------------------------
    # Altitude change event
    # -------------------------------------------------------------

    if (
        previous_altitude is not None
        and current_altitude is not None
    ):
        altitude_difference = (
            current_altitude
            - previous_altitude
        )

        if (
            abs(altitude_difference)
            >= ALTITUDE_CHANGE_THRESHOLD
        ):
            event_type = "ALTITUDE_CHANGE"

            if not event_is_on_cooldown(
                aircraft_hex,
                event_type,
            ):
                direction = (
                    "climbing"
                    if altitude_difference > 0
                    else "descending"
                )

                insert_event(
                    connection=connection,
                    event_time=observed_at,
                    event_type=event_type,
                    aircraft_hex=aircraft_hex,
                    region_code=region_code,
                    event_value=altitude_difference,
                    event_description=(
                        f"Aircraft is {direction}. "
                        f"Altitude changed by "
                        f"{altitude_difference:.0f} feet."
                    ),
                    source="aircraft_stream_processor",
                    event_payload={
                        "previous_altitude_baro": previous_altitude,
                        "current_altitude_baro": current_altitude,
                        "altitude_difference": altitude_difference,
                        "observation": observation,
                    },
                    run_id=run_id,
            )

                mark_event_created(
                    aircraft_hex,
                    event_type,
                )

    # -------------------------------------------------------------
    # Speed change event
    # -------------------------------------------------------------

    if (
        previous_speed is not None
        and current_speed is not None
    ):
        speed_difference = (
            current_speed
            - previous_speed
        )

        if (
            abs(speed_difference)
            >= SPEED_CHANGE_THRESHOLD
        ):
            event_type = "SPEED_CHANGE"

            if not event_is_on_cooldown(
                aircraft_hex,
                event_type,
            ):
                direction = (
                    "increased"
                    if speed_difference > 0
                    else "decreased"
                )

                insert_event(
                    connection=connection,
                    event_time=observed_at,
                    event_type=event_type,
                    aircraft_hex=aircraft_hex,
                    region_code=region_code,
                    event_value=speed_difference,
                    event_description=(
                        f"Ground speed {direction} by "
                        f"{speed_difference:.1f} knots."
                    ),
                    source="aircraft_stream_processor",
                    event_payload={
                        "previous_ground_speed": previous_speed,
                        "current_ground_speed": current_speed,
                        "speed_difference": speed_difference,
                        "observation": observation,
                    },
                    run_id=run_id,
            )

                mark_event_created(
                    aircraft_hex,
                    event_type,
                )

    # -------------------------------------------------------------
    # High vertical-rate event
    # -------------------------------------------------------------

    if current_vertical_rate is not None:

        if (
            abs(current_vertical_rate)
            >= VERTICAL_RATE_THRESHOLD
        ):
            event_type = "HIGH_VERTICAL_RATE"

            if not event_is_on_cooldown(
                aircraft_hex,
                event_type,
            ):
                direction = (
                    "climbing"
                    if current_vertical_rate > 0
                    else "descending"
                )

                insert_event(
                    connection=connection,
                    event_time=observed_at,
                    event_type=event_type,
                    aircraft_hex=aircraft_hex,
                    region_code=region_code,
                    event_value=current_vertical_rate,
                    event_description=(
                        f"Aircraft has a high vertical rate "
                        f"while {direction}: "
                        f"{current_vertical_rate:.0f} feet/minute."
                    ),
                    source="aircraft_stream_processor",
                    event_payload={
                        "vertical_rate": current_vertical_rate,
                        "observation": observation,
                    },
                    run_id=run_id,
            )

                mark_event_created(
                    aircraft_hex,
                    event_type,
                )

    # Update state after processing.
    previous_aircraft_state[
        aircraft_hex
    ] = current_state


# ---------------------------------------------------------------------
# Kafka consumer
# ---------------------------------------------------------------------

def create_kafka_consumer() -> Consumer:
    """
    Create the Redpanda Kafka consumer.
    """

    configuration = {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": KAFKA_GROUP_ID,
        "auto.offset.reset": "latest",
        "enable.auto.commit": True,
    }

    consumer = Consumer(
        configuration
    )

    consumer.subscribe([
        KAFKA_TOPIC
    ])

    logger.info(
        "Kafka consumer subscribed to topic '%s'.",
        KAFKA_TOPIC,
    )

    logger.info(
        "Consumer group: %s",
        KAFKA_GROUP_ID,
    )

    return consumer


def run_processor() -> None:
    """
    Main processor loop.
    """

    postgres_connection = None
    consumer = None

    try:
        postgres_connection = (
            create_postgres_connection()
        )

        consumer = create_kafka_consumer()

        logger.info(
            "Aircraft stream processor is running."
        )

        while running:

            message = consumer.poll(
                timeout=1.0
            )

            if message is None:
                continue

            if message.error():
                logger.error(
                    "Kafka message error: %s",
                    message.error(),
                )

                continue

            try:
                raw_value = message.value()

                if raw_value is None:
                    continue

                observation = json.loads(
                    raw_value.decode("utf-8")
                )

                if not isinstance(
                    observation,
                    dict,
                ):
                    logger.warning(
                        "Skipping message because it is "
                        "not a JSON object."
                    )
                    continue

                process_observation(
                    connection=postgres_connection,
                    observation=observation,
                )

            except json.JSONDecodeError:
                logger.exception(
                    "Invalid JSON message received."
                )

            except Exception:
                logger.exception(
                    "Error processing Kafka message."
                )

    except KafkaException:
        logger.exception(
            "Kafka error occurred."
        )

    except psycopg2.Error:
        logger.exception(
            "PostgreSQL error occurred."
        )

    except Exception:
        logger.exception(
            "Unexpected processor error."
        )

    finally:

        if consumer is not None:
            consumer.close()

            logger.info(
                "Kafka consumer closed."
            )

        if postgres_connection is not None:
            postgres_connection.close()

            logger.info(
                "PostgreSQL connection closed."
            )

        logger.info(
            "Aircraft stream processor stopped."
        )


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    run_processor()