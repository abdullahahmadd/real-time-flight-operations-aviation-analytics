-- ============================================================
-- Real-Time Flight Operations & Aviation Analytics
-- Run Tracking Migration
-- ============================================================

ALTER TABLE aviation.fact_aircraft_position
    ADD COLUMN IF NOT EXISTS run_id VARCHAR(40);

ALTER TABLE aviation.fact_aviation_event
    ADD COLUMN IF NOT EXISTS run_id VARCHAR(40);

CREATE INDEX IF NOT EXISTS idx_position_run_id
    ON aviation.fact_aircraft_position (run_id);

CREATE INDEX IF NOT EXISTS idx_event_run_id
    ON aviation.fact_aviation_event (run_id);