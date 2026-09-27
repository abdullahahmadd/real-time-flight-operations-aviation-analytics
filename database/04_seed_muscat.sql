-- ============================================================
-- Real-Time Flight Operations & Aviation Analytics
-- Muscat Region Seed
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
VALUES (
    'muscat',
    'Muscat Area',
    'OM',
    'Oman',
    21.000000,
    25.500000,
    56.000000,
    60.500000
)
ON CONFLICT (region_code) DO NOTHING;