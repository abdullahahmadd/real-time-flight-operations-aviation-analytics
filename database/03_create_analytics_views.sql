--
-- PostgreSQL database dump
--

\restrict oXVHvAlCp5uFjCBzYf14cdYNdltd8ToBXkjdGJADni2Ds6uiS2LgVYMmyOZi5Tt

-- Dumped from database version 16.15 (Debian 16.15-1.pgdg13+2)
-- Dumped by pg_dump version 16.15 (Debian 16.15-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: analytics; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA analytics;


--
-- Name: v_current_run; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_current_run AS
 SELECT max((run_id)::text) AS run_id
   FROM aviation.fact_aircraft_position
  WHERE (run_id IS NOT NULL);


--
-- Name: v_aircraft_summary; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_aircraft_summary AS
 SELECT aircraft_hex,
    max((callsign)::text) AS callsign,
    max((registration)::text) AS registration,
    max((aircraft_type)::text) AS aircraft_type,
    max((category)::text) AS category,
    count(*) AS position_count,
    count(DISTINCT region_code) AS regions_observed,
    min(observed_at) AS first_observation,
    max(observed_at) AS last_observation,
    round(avg(altitude_baro), 2) AS avg_altitude_baro,
    round(avg(ground_speed), 2) AS avg_ground_speed,
    max(altitude_baro) AS max_altitude_baro,
    max(ground_speed) AS max_ground_speed,
    round(avg(abs(vertical_rate)), 2) AS avg_abs_vertical_rate
   FROM aviation.fact_aircraft_position p
  WHERE (((run_id)::text = ( SELECT v_current_run.run_id
           FROM analytics.v_current_run)) AND (aircraft_hex IS NOT NULL) AND (TRIM(BOTH FROM aircraft_hex) <> ''::text))
  GROUP BY aircraft_hex
  ORDER BY (count(*)) DESC;


--
-- Name: v_current_aircraft; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_current_aircraft AS
 WITH ranked_aircraft AS (
         SELECT p.aircraft_hex,
            p.aircraft_id,
            p.callsign,
            p.registration,
            p.aircraft_type,
            p.latitude,
            p.longitude,
            p.altitude_baro,
            p.altitude_geom,
            p.ground_speed,
            p.track,
            p.vertical_rate,
            p.squawk,
            p.category,
            p.emergency_status,
            p.source,
            p.region_code,
            p.observed_at,
            row_number() OVER (PARTITION BY p.aircraft_hex ORDER BY p.observed_at DESC) AS latest_rank
           FROM aviation.fact_aircraft_position p
          WHERE ((p.run_id)::text = ( SELECT v_current_run.run_id
                   FROM analytics.v_current_run))
        )
 SELECT aircraft_hex,
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
    observed_at,
    latest_rank
   FROM ranked_aircraft
  WHERE (latest_rank = 1);


--
-- Name: v_event_summary; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_event_summary AS
 SELECT event_type,
    region_code,
    count(*) AS event_count,
    count(DISTINCT aircraft_hex) AS unique_aircraft,
    min(event_time) AS first_event,
    max(event_time) AS last_event,
    round(avg(event_value), 2) AS avg_event_value,
    max(event_value) AS max_event_value
   FROM aviation.fact_aviation_event e
  WHERE ((run_id)::text = ( SELECT v_current_run.run_id
           FROM analytics.v_current_run))
  GROUP BY event_type, region_code
  ORDER BY (count(*)) DESC;


--
-- Name: v_recent_events; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_recent_events AS
 SELECT event_id,
    event_time,
    event_type,
    aircraft_hex,
    region_code,
    event_value,
    event_description,
    source,
    event_payload
   FROM aviation.fact_aviation_event e
  WHERE ((run_id)::text = ( SELECT v_current_run.run_id
           FROM analytics.v_current_run))
  ORDER BY event_time DESC;


--
-- Name: v_region_movements; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_region_movements AS
 SELECT (event_payload ->> 'previous_region'::text) AS previous_region,
    (event_payload ->> 'current_region'::text) AS current_region,
    count(*) AS movement_count,
    count(DISTINCT aircraft_hex) AS unique_aircraft,
    min(event_time) AS first_movement,
    max(event_time) AS last_movement
   FROM aviation.fact_aviation_event
  WHERE (((run_id)::text = ( SELECT v_current_run.run_id
           FROM analytics.v_current_run)) AND ((event_type)::text = 'REGION_CHANGE'::text) AND ((event_payload ->> 'previous_region'::text) IS NOT NULL) AND ((event_payload ->> 'current_region'::text) IS NOT NULL))
  GROUP BY (event_payload ->> 'previous_region'::text), (event_payload ->> 'current_region'::text);


--
-- Name: v_regional_traffic_summary; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_regional_traffic_summary AS
 SELECT region_code,
    count(*) AS position_count,
    count(DISTINCT aircraft_hex) AS unique_aircraft,
    min(observed_at) AS first_observation,
    max(observed_at) AS last_observation,
    round(avg(altitude_baro), 2) AS avg_altitude_baro,
    round(avg(ground_speed), 2) AS avg_ground_speed,
    max(altitude_baro) AS max_altitude_baro,
    max(ground_speed) AS max_ground_speed
   FROM aviation.fact_aircraft_position p
  WHERE (((run_id)::text = ( SELECT v_current_run.run_id
           FROM analytics.v_current_run)) AND (region_code IS NOT NULL) AND (TRIM(BOTH FROM region_code) <> ''::text))
  GROUP BY region_code
  ORDER BY (count(*)) DESC;


--
-- Name: v_traffic_timeseries; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.v_traffic_timeseries AS
 SELECT date_bin('00:05:00'::interval, observed_at, '2000-01-01 00:00:00+00'::timestamp with time zone) AS time_bucket,
    region_code,
    count(*) AS position_count,
    count(DISTINCT aircraft_hex) AS unique_aircraft,
    round(avg(altitude_baro), 2) AS avg_altitude_baro,
    round(avg(ground_speed), 2) AS avg_ground_speed,
    max(altitude_baro) AS max_altitude_baro,
    max(ground_speed) AS max_ground_speed
   FROM aviation.fact_aircraft_position p
  WHERE (((run_id)::text = ( SELECT v_current_run.run_id
           FROM analytics.v_current_run)) AND (region_code IS NOT NULL) AND (TRIM(BOTH FROM region_code) <> ''::text))
  GROUP BY (date_bin('00:05:00'::interval, observed_at, '2000-01-01 00:00:00+00'::timestamp with time zone)), region_code
  ORDER BY (date_bin('00:05:00'::interval, observed_at, '2000-01-01 00:00:00+00'::timestamp with time zone)), region_code;


--
-- PostgreSQL database dump complete
--

\unrestrict oXVHvAlCp5uFjCBzYf14cdYNdltd8ToBXkjdGJADni2Ds6uiS2LgVYMmyOZi5Tt

