from pathlib import Path

import os

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# =========================================================
# PROJECT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Real-Time Flight Operations API",
    description=(
        "Backend API for the Real-Time Flight Operations "
        "& Aviation Analytics platform"
    ),
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
).strip()
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        dbname=os.getenv(
            "POSTGRES_DB",
            "flight_analytics",
        ),
        user=os.getenv(
            "POSTGRES_USER",
            "flight_analytics",
        ),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


# =========================================================
# HELPER — FETCH VIEW DATA
# =========================================================

def fetch_view(view_name, limit=None):
    """
    Read rows directly from an existing PostgreSQL
    analytics view and return them as dictionaries.

    The analytics views remain the source of truth.
    """

    query = f"""
        SELECT *
        FROM {view_name}
    """

    if limit is not None:
        query += f"""
        LIMIT {int(limit)}
        """

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)

            columns = [
                column.name
                for column in cursor.description
            ]

            rows = cursor.fetchall()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "application": (
            "Real-Time Flight Operations "
            "& Aviation Analytics"
        ),
        "status": "online",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "aviation-api",
    }


# =========================================================
# DATABASE STATUS
# =========================================================

@app.get("/api/database")
def database_status():

    try:

        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute("SELECT 1;")

                result = cursor.fetchone()

        return {
            "status": "connected",
            "database": os.getenv(
                "POSTGRES_DB",
                "flight_analytics",
            ),
            "result": result[0],
        }

    except Exception as exc:

        return {
            "status": "error",
            "message": str(exc),
        }


# =========================================================
# OVERVIEW
# =========================================================

@app.get("/api/overview")
def overview():

    with get_db_connection() as connection:

        with connection.cursor() as cursor:

            # -------------------------------------------------
            # Current aircraft
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM analytics.v_current_aircraft;
                """
            )

            active_aircraft = cursor.fetchone()[0]

            # -------------------------------------------------
            # Current-run events
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(event_count), 0)
                        AS total_events,

                    COALESCE(
                        SUM(event_count)
                        FILTER (
                            WHERE event_type = 'REGION_CHANGE'
                        ),
                        0
                    )
                        AS region_changes,

                    COALESCE(
                        SUM(event_count)
                        FILTER (
                            WHERE event_type = 'ALTITUDE_CHANGE'
                        ),
                        0
                    )
                        AS altitude_changes,

                    COALESCE(
                        SUM(event_count)
                        FILTER (
                            WHERE event_type = 'HIGH_VERTICAL_RATE'
                        ),
                        0
                    )
                        AS high_vertical_rate_events

                FROM analytics.v_event_summary;
                """
            )

            row = cursor.fetchone()

    return {
        "active_aircraft": active_aircraft,
        "total_events": row[0],
        "region_changes": row[1],
        "altitude_changes": row[2],
        "high_vertical_rate_events": row[3],
    }


# =========================================================
# REGIONAL TRAFFIC
# =========================================================

@app.get("/api/regional")
def regional():

    data = fetch_view(
        "analytics.v_regional_traffic_summary"
    )

    return {
        "count": len(data),
        "data": data,
    }


# =========================================================
# CURRENT AIRCRAFT
# =========================================================

@app.get("/api/aircraft")
def aircraft():

    data = fetch_view(
        "analytics.v_current_aircraft",
        limit=1000,
    )

    return {
        "count": len(data),
        "data": data,
    }


# =========================================================
# AIRCRAFT SUMMARY
# =========================================================

@app.get("/api/aircraft/summary")
def aircraft_summary():

    data = fetch_view(
        "analytics.v_aircraft_summary",
        limit=1000,
    )

    return {
        "count": len(data),
        "data": data,
    }


# =========================================================
# RECENT EVENTS
# =========================================================

@app.get("/api/events")
def events():

    data = fetch_view(
        "analytics.v_recent_events",
        limit=500,
    )

    return {
        "count": len(data),
        "data": data,
    }


# =========================================================
# EVENT SUMMARY
# =========================================================

@app.get("/api/events/summary")
def events_summary():

    data = fetch_view(
        "analytics.v_event_summary"
    )

    return {
        "count": len(data),
        "data": data,
    }


# =========================================================
# TRAFFIC TIME SERIES
# =========================================================

@app.get("/api/timeseries")
def timeseries():

    data = fetch_view(
        "analytics.v_traffic_timeseries",
        limit=1000,
    )

    return {
        "count": len(data),
        "data": data,
    }


# =========================================================
# REGION MOVEMENTS
# =========================================================

@app.get("/api/movements")
def movements():

    data = fetch_view(
        "analytics.v_region_movements",
        limit=500,
    )

    return {
        "count": len(data),
        "data": data,
    }


# =========================================================
# RECENT EVENT + MOVEMENT DATA
# =========================================================

@app.get("/api/operations")
def operations():

    aircraft_data = fetch_view(
        "analytics.v_current_aircraft",
        limit=1000,
    )

    event_data = fetch_view(
        "analytics.v_recent_events",
        limit=100,
    )

    movement_data = fetch_view(
        "analytics.v_region_movements",
        limit=100,
    )

    return {
        "aircraft": {
            "count": len(aircraft_data),
            "data": aircraft_data,
        },
        "events": {
            "count": len(event_data),
            "data": event_data,
        },
        "movements": {
            "count": len(movement_data),
            "data": movement_data,
        },
    }