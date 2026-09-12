-- ============================================================
-- Real-Time Flight Operations & Aviation Analytics
-- PostgreSQL Database Schema
-- ============================================================

CREATE SCHEMA IF NOT EXISTS aviation;

-- ============================================================
-- Dimension: Aircraft
-- ============================================================

CREATE TABLE IF NOT EXISTS aviation.dim_aircraft (
    aircraft_id BIGSERIAL PRIMARY KEY,
    aircraft_hex VARCHAR(20) NOT NULL UNIQUE,
    registration VARCHAR(20),
    aircraft_type VARCHAR(20),
    aircraft_description VARCHAR(255),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    operator VARCHAR(150),
    first_seen_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Dimension: Region
-- ============================================================

CREATE TABLE IF NOT EXISTS aviation.dim_region (
    region_id SERIAL PRIMARY KEY,
    region_code VARCHAR(50) NOT NULL UNIQUE,
    region_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(10),
    country_name VARCHAR(100),
    min_latitude NUMERIC(9, 6),
    max_latitude NUMERIC(9, 6),
    min_longitude NUMERIC(9, 6),
    max_longitude NUMERIC(9, 6),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Fact: Aircraft Position Observations
-- ============================================================

CREATE TABLE IF NOT EXISTS aviation.fact_aircraft_position (
    position_id BIGSERIAL PRIMARY KEY,
    observed_at TIMESTAMPTZ NOT NULL,
    aircraft_hex VARCHAR(20) NOT NULL,
    aircraft_id BIGINT,
    callsign VARCHAR(20),
    registration VARCHAR(20),
    aircraft_type VARCHAR(20),

    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),

    altitude_baro NUMERIC(10, 2),
    altitude_geom NUMERIC(10, 2),
    ground_speed NUMERIC(10, 2),
    track NUMERIC(7, 2),
    vertical_rate NUMERIC(10, 2),

    squawk VARCHAR(10),
    category VARCHAR(10),
    emergency_status VARCHAR(50),

    source VARCHAR(50),
    region_code VARCHAR(50),

    raw_event JSONB,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_position_aircraft
        FOREIGN KEY (aircraft_id)
        REFERENCES aviation.dim_aircraft (aircraft_id)
);

-- ============================================================
-- Fact: Aviation Events
-- ============================================================

CREATE TABLE IF NOT EXISTS aviation.fact_aviation_event (
    event_id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(100) NOT NULL,

    aircraft_hex VARCHAR(20),
    region_code VARCHAR(50),

    event_value NUMERIC(18, 4),
    event_description TEXT,

    source VARCHAR(50),
    event_payload JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_position_observed_at
    ON aviation.fact_aircraft_position (observed_at);

CREATE INDEX IF NOT EXISTS idx_position_aircraft_hex
    ON aviation.fact_aircraft_position (aircraft_hex);

CREATE INDEX IF NOT EXISTS idx_position_region_code
    ON aviation.fact_aircraft_position (region_code);

CREATE INDEX IF NOT EXISTS idx_position_lat_lon
    ON aviation.fact_aircraft_position (latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_event_time
    ON aviation.fact_aviation_event (event_time);

CREATE INDEX IF NOT EXISTS idx_event_type
    ON aviation.fact_aviation_event (event_type);

CREATE INDEX IF NOT EXISTS idx_event_aircraft_hex
    ON aviation.fact_aviation_event (aircraft_hex);

-- ============================================================
-- Initial Regions
-- ============================================================

INSERT INTO aviation.dim_region (
    region_code,
    region_name,
    country_code,
    country_name,
    min_latitude,
    max_latitude,
    min_longitude,
    max_longitude
)
VALUES
(
    'ksa',
    'Saudi Arabia',
    'SA',
    'Saudi Arabia',
    16.000000,
    33.000000,
    34.000000,
    56.000000
),
(
    'riyadh',
    'Riyadh Area',
    'SA',
    'Saudi Arabia',
    23.000000,
    26.500000,
    43.000000,
    48.500000
),
(
    'jeddah',
    'Jeddah Area',
    'SA',
    'Saudi Arabia',
    20.000000,
    23.500000,
    37.000000,
    40.000000
),
(
    'dammam',
    'Dammam Area',
    'SA',
    'Saudi Arabia',
    25.000000,
    27.500000,
    49.000000,
    51.500000
),
(
    'dubai',
    'Dubai Area',
    'AE',
    'United Arab Emirates',
    24.000000,
    26.500000,
    54.000000,
    56.500000
),
(
    'doha',
    'Doha Area',
    'QA',
    'Qatar',
    24.000000,
    26.500000,
    50.000000,
    52.000000
)
ON CONFLICT (region_code) DO NOTHING;