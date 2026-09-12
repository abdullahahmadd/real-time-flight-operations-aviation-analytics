"""
ADSB.lol aircraft data client.

Responsibilities:
- Fetch aircraft data from ADSB.lol
- Handle temporary API failures with retries
- Normalize ADSB.lol's "ac" field to project-standard "aircraft"
- Save successful snapshots as JSON
- Provide useful logging
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
import os


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIRECTORY = PROJECT_ROOT / "data" / "samples"
SNAPSHOT_FILE = SAMPLES_DIRECTORY / "live_aircraft_snapshot.json"


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

ADSB_BASE_URL = os.getenv(
    "ADSB_BASE_URL",
    "https://api.adsb.lol",
).rstrip("/")


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTTP configuration
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY_SECONDS = 10

USER_AGENT = (
    "Real-Time-Flight-Operations-Analytics/1.0 "
    "(educational portfolio project)"
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def build_endpoint(endpoint: str) -> str:
    """
    Build a complete ADSB.lol URL.

    Examples:
        /v2/aircraft
        /v2/lat/24.7136/lon/46.6753/dist/250
    """

    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    return f"{ADSB_BASE_URL}{endpoint}"


def normalize_aircraft_response(
    response_data: dict[str, Any],
    endpoint: str,
) -> dict[str, Any]:
    """
    Normalize the ADSB.lol response.

    ADSB.lol normally returns aircraft in:
        response_data["ac"]

    Our project will consistently use:
        normalized_data["aircraft"]
    """

    raw_aircraft = response_data.get("ac", [])

    if not isinstance(raw_aircraft, list):
        logger.warning(
            "Unexpected aircraft field type: %s",
            type(raw_aircraft).__name__,
        )
        raw_aircraft = []

    normalized_data = dict(response_data)

    # Keep the original ADSB.lol field and add our project-standard field.
    normalized_data["aircraft"] = raw_aircraft

    # Add project metadata.
    normalized_data["source"] = "ADSB.lol"
    normalized_data["source_endpoint"] = build_endpoint(endpoint)
    normalized_data["retrieved_at_utc"] = datetime.now(
        timezone.utc
    ).isoformat()

    normalized_data["aircraft_count"] = len(raw_aircraft)

    return normalized_data


def save_snapshot(snapshot: dict[str, Any]) -> Path:
    """
    Save a normalized aircraft snapshot to data/samples.
    """

    SAMPLES_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with SNAPSHOT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            snapshot,
            file,
            indent=2,
            ensure_ascii=False,
        )

    logger.info(
        "Snapshot saved to: %s",
        SNAPSHOT_FILE,
    )

    return SNAPSHOT_FILE


# ---------------------------------------------------------------------------
# Main API function
# ---------------------------------------------------------------------------

def fetch_aircraft_snapshot(
    endpoint: str = "/v2/aircraft",
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
    retry_delay_seconds: int = DEFAULT_RETRY_DELAY_SECONDS,
    save_to_file: bool = True,
) -> dict[str, Any]:
    """
    Fetch and normalize aircraft data from ADSB.lol.

    Parameters:
        endpoint:
            ADSB.lol API endpoint.

        timeout:
            HTTP timeout in seconds.

        retry_attempts:
            Number of attempts after temporary failures.

        retry_delay_seconds:
            Initial delay between retries.

        save_to_file:
            Whether to save the normalized snapshot as JSON.

    Returns:
        Normalized aircraft snapshot dictionary.

    Raises:
        RuntimeError:
            If ADSB.lol remains unavailable after all attempts.
    """

    url = build_endpoint(endpoint)

    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }

    logger.info(
        "Fetching aircraft data from: %s",
        url,
    )

    last_error: Exception | None = None

    for attempt in range(1, retry_attempts + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout,
            )

            response.raise_for_status()

            response_data = response.json()

            if not isinstance(response_data, dict):
                raise RuntimeError(
                    "ADSB.lol returned an unexpected JSON structure."
                )

            normalized_data = normalize_aircraft_response(
                response_data=response_data,
                endpoint=endpoint,
            )

            aircraft_count = normalized_data["aircraft_count"]

            logger.info(
                "Successfully fetched aircraft snapshot: %s aircraft.",
                aircraft_count,
            )

            if save_to_file:
                save_snapshot(normalized_data)

            return normalized_data

        except requests.exceptions.RequestException as error:
            last_error = error

            if attempt < retry_attempts:
                delay = retry_delay_seconds * attempt

                logger.warning(
                    "ADSB.lol temporarily unavailable "
                    "(attempt %s/%s).",
                    attempt,
                    retry_attempts,
                )

                logger.info(
                    "Retrying in %s seconds...",
                    delay,
                )

                time.sleep(delay)

            else:
                logger.error(
                    "ADSB.lol request failed after %s attempts.",
                    retry_attempts,
                )

        except ValueError as error:
            last_error = error

            logger.error(
                "ADSB.lol returned invalid JSON: %s",
                error,
            )

            break

        except Exception as error:
            last_error = error

            logger.error(
                "Unexpected error while fetching aircraft data: %s",
                error,
            )

            break

    raise RuntimeError(
        f"ADSB.lol remained unavailable after "
        f"{retry_attempts} attempts."
    ) from last_error


# ---------------------------------------------------------------------------
# Command-line execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    snapshot = fetch_aircraft_snapshot()

    aircraft = snapshot.get("aircraft", [])

    print()
    print("ADSB.lol snapshot fetched successfully.")
    print(f"Endpoint: {snapshot.get('source_endpoint')}")
    print(f"Aircraft: {len(aircraft)}")
    print(f"Saved to: {SNAPSHOT_FILE}")