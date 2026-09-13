"""
PostgreSQL loader for the Real-Time Flight Operations & Aviation Analytics project.

Pipeline:

ADSB.lol API
    ↓
Python ingestion client
    ↓
PostgreSQL
    ├── aviation.dim_aircraft
    └── aviation.fact_aircraft_position
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from ingestion.adsb_client import fetch_aircraft_snapshot
from ingestion.config import REGIONS


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5433"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "flight_analytics")
POSTGRES_USER = os.getenv("POSTGRES_USER", "flight_analytics")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_me")


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    """
    Return the current UTC timestamp with timezone information.
    """
    return datetime.now(timezone.utc)


def clean_text(value: Any) -> str | None:
    """
    Convert a value to a cleaned string.

    Empty strings and the literal values 'none', 'null', and 'nan'
    are converted to None.
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    if text.lower() in {"none", "null", "nan"}:
        return None

    return text


def clean_decimal(value: Any) -> Decimal | None:
    """
    Convert numeric values into Decimal values suitable for PostgreSQL NUMERIC.

    Invalid, missing, or special values return None.
    """
    if value is None:
        return None

    try:
        decimal_value = Decimal(str(value))

        if not decimal_value.is_finite():
            return None

        return decimal_value

    except (InvalidOperation, ValueError, TypeError):
        return None


def clean_aircraft_hex(
    aircraft: dict[str, Any],
) -> str | None:
    """
    Extract and normalize the aircraft ICAO hex identifier.
    """
    aircraft_hex = clean_text(aircraft.get("hex"))

    if aircraft_hex is None:
        return None

    return aircraft_hex.lower()


def clean_callsign(
    aircraft: dict[str, Any],
) -> str | None:
    """
    Extract and normalize the flight callsign.

    ADSB.lol commonly returns callsigns with trailing spaces.
    """
    flight = aircraft.get("flight")

    if flight is None:
        return None

    return clean_text(flight)


def get_aircraft_type(
    aircraft: dict[str, Any],
) -> str | None:
    """
    Extract aircraft type code.
    """
    return clean_text(aircraft.get("t"))


def get_registration(
    aircraft: dict[str, Any],
) -> str | None:
    """
    Extract aircraft registration.
    """
    return clean_text(aircraft.get("r"))


def get_source(
    aircraft: dict[str, Any],
    snapshot: dict[str, Any],
) -> str:
    """
    Determine the source label for the position record.
    """
    source = clean_text(aircraft.get("source"))

    if source:
        return source

    snapshot_source = clean_text(snapshot.get("source"))

    if snapshot_source:
        return snapshot_source

    return "adsb.lol"


# ---------------------------------------------------------------------------
# PostgreSQL connection
# ---------------------------------------------------------------------------

def get_connection():
    """
    Create a PostgreSQL connection using environment configuration.
    """
    logger.info(
        "Connecting to PostgreSQL at %s:%s/%s",
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DB,
    )

    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        connect_timeout=10,
    )


# ---------------------------------------------------------------------------
# Region lookup
# ---------------------------------------------------------------------------

def get_region_id(
    cursor,
    region_code: str,
) -> int:
    """
    Return the database region_id for a region code.
    """
    cursor.execute(
        """
        SELECT region_id
        FROM aviation.dim_region
        WHERE LOWER(region_code) = LOWER(%s)
        """,
        (region_code,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(
            f"Region code '{region_code}' was not found "
            "in aviation.dim_region"
        )

    return int(result["region_id"])


# ---------------------------------------------------------------------------
# Aircraft dimension loading
# ---------------------------------------------------------------------------

def upsert_aircraft_dimension(
    cursor,
    aircraft: dict[str, Any],
    observed_at: datetime,
) -> int | None:
    """
    Insert or update an aircraft in aviation.dim_aircraft.

    The aircraft_hex field is used as the natural business key.

    Returns:
        The generated aircraft_id, or None if the aircraft
        has no hex value.
    """
    aircraft_hex = clean_aircraft_hex(aircraft)

    if aircraft_hex is None:
        logger.warning("Skipping aircraft without hex identifier")
        return None

    registration = get_registration(aircraft)
    aircraft_type = get_aircraft_type(aircraft)

    cursor.execute(
        """
        INSERT INTO aviation.dim_aircraft (
            aircraft_hex,
            registration,
            aircraft_type,
            first_seen_at,
            last_seen_at,
            created_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (aircraft_hex)
        DO UPDATE SET
            registration = COALESCE(
                EXCLUDED.registration,
                aviation.dim_aircraft.registration
            ),
            aircraft_type = COALESCE(
                EXCLUDED.aircraft_type,
                aviation.dim_aircraft.aircraft_type
            ),
            last_seen_at = EXCLUDED.last_seen_at,
            updated_at = EXCLUDED.updated_at
        RETURNING aircraft_id
        """,
        (
            aircraft_hex,
            registration,
            aircraft_type,
            observed_at,
            observed_at,
            observed_at,
            observed_at,
        ),
    )

    result = cursor.fetchone()

    if result is None:
        return None

    return int(result["aircraft_id"])


# ---------------------------------------------------------------------------
# Aircraft position loading
# ---------------------------------------------------------------------------

def insert_aircraft_position(
    cursor,
    aircraft: dict[str, Any],
    aircraft_id: int,
    region_id: int,
    region_code: str,
    snapshot: dict[str, Any],
    observed_at: datetime,
) -> bool:
    """
    Insert one aircraft position record into
    aviation.fact_aircraft_position.

    Returns:
        True if a position record was inserted.
        False if the aircraft has no valid latitude or longitude.
    """
    latitude = clean_decimal(aircraft.get("lat"))
    longitude = clean_decimal(aircraft.get("lon"))

    if latitude is None or longitude is None:
        logger.debug(
            "Skipping aircraft %s because latitude or longitude is missing",
            aircraft.get("hex"),
        )
        return False

    aircraft_hex = clean_aircraft_hex(aircraft)

    if aircraft_hex is None:
        logger.debug(
            "Skipping aircraft because aircraft hex is missing"
        )
        return False

    callsign = clean_callsign(aircraft)
    registration = get_registration(aircraft)
    aircraft_type = get_aircraft_type(aircraft)

    altitude_baro = clean_decimal(aircraft.get("alt_baro"))
    altitude_geom = clean_decimal(aircraft.get("alt_geom"))
    ground_speed = clean_decimal(aircraft.get("gs"))
    track = clean_decimal(aircraft.get("track"))
    vertical_rate = clean_decimal(aircraft.get("baro_rate"))

    squawk = clean_text(aircraft.get("squawk"))
    category = clean_text(aircraft.get("category"))
    emergency_status = clean_text(aircraft.get("emergency"))

    source = get_source(aircraft, snapshot)

    cursor.execute(
        """
        INSERT INTO aviation.fact_aircraft_position (
            observed_at,
            aircraft_hex,
            aircraft_id,
            callsign,
            registration,
            aircraft_type,
            latitude,
            longitude,
            altitude_baro,
            altitude_geom,
            ground_speed,
            track,
            vertical_rate,
            squawk,
            category,
            emergency_status,
            source,
            region_code
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
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            observed_at,
            aircraft_hex,
            aircraft_id,
            callsign,
            registration,
            aircraft_type,
            latitude,
            longitude,
            altitude_baro,
            altitude_geom,
            ground_speed,
            track,
            vertical_rate,
            squawk,
            category,
            emergency_status,
            source,
            region_code,
        ),
    )

    return True


# ---------------------------------------------------------------------------
# Snapshot loading
# ---------------------------------------------------------------------------

def load_snapshot_to_postgres(
    snapshot: dict[str, Any],
    region_code: str,
) -> dict[str, int]:
    """
    Load one ADSB.lol snapshot into PostgreSQL.

    Returns a summary containing:
        aircraft_received
        aircraft_dimension_upserted
        positions_inserted
        aircraft_skipped
    """
    aircraft_list = snapshot.get("aircraft", [])

    if not isinstance(aircraft_list, list):
        raise ValueError(
            "Snapshot field 'aircraft' is not a list"
        )

    region_code = str(region_code).strip().lower()

    observed_at = utc_now()

    summary = {
        "aircraft_received": len(aircraft_list),
        "aircraft_dimension_upserted": 0,
        "positions_inserted": 0,
        "aircraft_skipped": 0,
    }

    connection = None

    try:
        connection = get_connection()

        with connection:
            with connection.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:

                region_id = get_region_id(
                    cursor,
                    region_code,
                )

                for aircraft in aircraft_list:

                    if not isinstance(aircraft, dict):
                        summary["aircraft_skipped"] += 1
                        continue

                    try:
                        aircraft_id = upsert_aircraft_dimension(
                            cursor=cursor,
                            aircraft=aircraft,
                            observed_at=observed_at,
                        )

                        if aircraft_id is None:
                            summary["aircraft_skipped"] += 1
                            continue

                        summary[
                            "aircraft_dimension_upserted"
                        ] += 1

                        inserted = insert_aircraft_position(
                            cursor=cursor,
                            aircraft=aircraft,
                            aircraft_id=aircraft_id,
                            region_id=region_id,
                            region_code=region_code,
                            snapshot=snapshot,
                            observed_at=observed_at,
                        )

                        if inserted:
                            summary["positions_inserted"] += 1
                        else:
                            summary["aircraft_skipped"] += 1

                    except Exception:
                        logger.exception(
                            "Failed to load aircraft with hex '%s'",
                            aircraft.get("hex"),
                        )

                        summary["aircraft_skipped"] += 1

        logger.info(
            "Loaded region '%s': received=%s, "
            "dimension_upserted=%s, positions=%s, skipped=%s",
            region_code,
            summary["aircraft_received"],
            summary["aircraft_dimension_upserted"],
            summary["positions_inserted"],
            summary["aircraft_skipped"],
        )

        return summary

    except OperationalError:
        logger.exception(
            "PostgreSQL connection or operation failed"
        )
        raise

    finally:
        if connection is not None:
            connection.close()


# ---------------------------------------------------------------------------
# Regional ingestion
# ---------------------------------------------------------------------------

def load_region_snapshot(
    region: dict[str, Any],
) -> dict[str, int]:
    """
    Fetch and load one region snapshot.
    """
    region_code = str(
        region["region_code"]
    ).strip().lower()

    region_name = region["region_name"]
    endpoint = region["endpoint"]

    logger.info(
        "Fetching live aircraft data for %s (%s)",
        region_name,
        region_code,
    )

    snapshot = fetch_aircraft_snapshot(
        endpoint=endpoint,
        save_to_file=False,
    )

    return load_snapshot_to_postgres(
        snapshot=snapshot,
        region_code=region_code,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Load one live snapshot for every configured region.
    """
    logger.info(
        "Starting ADSB.lol to PostgreSQL loading process"
    )

    total_summary = {
        "aircraft_received": 0,
        "aircraft_dimension_upserted": 0,
        "positions_inserted": 0,
        "aircraft_skipped": 0,
    }

    for region in REGIONS:
        region_code = region["region_code"]
        region_name = region["region_name"]

        try:
            summary = load_region_snapshot(region)

            for key in total_summary:
                total_summary[key] += summary[key]

        except Exception:
            logger.exception(
                "Failed to load region '%s' (%s)",
                region_name,
                region_code,
            )

    logger.info(
        "PostgreSQL loading process completed"
    )

    logger.info(
        "Total summary: %s",
        total_summary,
    )

    print()
    print("PostgreSQL loading completed")
    print("--------------------------------")
    print(
        f"Aircraft received:          "
        f"{total_summary['aircraft_received']}"
    )
    print(
        f"Aircraft dimension upserted: "
        f"{total_summary['aircraft_dimension_upserted']}"
    )
    print(
        f"Positions inserted:         "
        f"{total_summary['positions_inserted']}"
    )
    print(
        f"Aircraft skipped:           "
        f"{total_summary['aircraft_skipped']}"
    )


if __name__ == "__main__":
    main()