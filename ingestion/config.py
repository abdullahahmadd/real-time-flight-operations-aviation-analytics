"""
Application configuration for the Real-Time Flight Operations & Aviation Analytics project.
"""

from pathlib import Path
import os

from dotenv import load_dotenv


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLES_DATA_DIR = DATA_DIR / "samples"


# ---------------------------------------------------------
# Environment variables
# ---------------------------------------------------------

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# Application settings
# ---------------------------------------------------------

APP_ENV = os.getenv("APP_ENV", "development")


# ---------------------------------------------------------
# ADSB.lol settings
# ---------------------------------------------------------

ADSB_BASE_URL = os.getenv(
    "ADSB_BASE_URL",
    "https://api.adsb.lol",
)

ADSB_TIMEOUT_SECONDS = int(
    os.getenv("ADSB_TIMEOUT_SECONDS", "30")
)

ADSB_MAX_RETRIES = int(
    os.getenv("ADSB_MAX_RETRIES", "3")
)

ADSB_RETRY_DELAY_SECONDS = int(
    os.getenv("ADSB_RETRY_DELAY_SECONDS", "10")
)


# ---------------------------------------------------------
# Regional aircraft endpoints
# ---------------------------------------------------------
#
# The endpoint format is:
#
# /v2/lat/<latitude>/lon/<longitude>/dist/<distance>
#
# Distance is measured in nautical miles.
#
# These are regional observation areas, not exact city boundaries.
#


REGIONS = [
    {
        "region_code": "riyadh",
        "region_name": "Riyadh",
        "country_code": "SA",
        "latitude": 24.7136,
        "longitude": 46.6753,
        "distance_nm": 250,
        "endpoint": "/v2/lat/24.7136/lon/46.6753/dist/250",
    },
    {
        "region_code": "dammam",
        "region_name": "Dammam",
        "country_code": "SA",
        "latitude": 26.4207,
        "longitude": 50.0888,
        "distance_nm": 250,
        "endpoint": "/v2/lat/26.4207/lon/50.0888/dist/250",
    },
    {
        "region_code": "dubai",
        "region_name": "Dubai",
        "country_code": "AE",
        "latitude": 25.2048,
        "longitude": 55.2708,
        "distance_nm": 250,
        "endpoint": "/v2/lat/25.2048/lon/55.2708/dist/250",
    },
    {
        "region_code": "doha",
        "region_name": "Doha",
        "country_code": "QA",
        "latitude": 25.2854,
        "longitude": 51.5310,
        "distance_nm": 250,
        "endpoint": "/v2/lat/25.2854/lon/51.5310/dist/250",
    },
    {
        "region_code": "muscat",
        "region_name": "Muscat",
        "country_code": "OM",
        "latitude": 23.5880,
        "longitude": 58.3829,
        "distance_nm": 250,
        "endpoint": "/v2/lat/23.5880/lon/58.3829/dist/250",
    },
    {
        "region_code": "manama",
        "region_name": "Manama",
        "country_code": "BH",
        "latitude": 26.2235,
        "longitude": 50.5876,
        "distance_nm": 250,
        "endpoint": "/v2/lat/26.2235/lon/50.5876/dist/250",
    },
    {
        "region_code": "kuwait_city",
        "region_name": "Kuwait City",
        "country_code": "KW",
        "latitude": 29.3759,
        "longitude": 47.9774,
        "distance_nm": 250,
        "endpoint": "/v2/lat/29.3759/lon/47.9774/dist/250",
    },
]

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------


def get_region_by_code(region_code: str) -> dict | None:
    """
    Return one region configuration by its region code.
    """

    for region in REGIONS:
        if region["region_code"] == region_code:
            return region

    return None


def get_region_endpoint(region: dict) -> str:
    """
    Build the complete ADSB.lol URL for a region.
    """

    endpoint = region["endpoint"]

    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint

    return f"{ADSB_BASE_URL}{endpoint}"


def ensure_project_directories() -> None:
    """
    Create required project directories if they do not exist.
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLES_DATA_DIR.mkdir(parents=True, exist_ok=True)