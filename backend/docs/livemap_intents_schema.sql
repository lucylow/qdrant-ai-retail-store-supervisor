-- LiveMap intents table: privacy-by-design schema (draft)
--
-- This migration is provided as a reference for a relational database
-- such as Postgres. The current hackathon prototype keeps intents
-- in-memory, but production deployments should persist them with a
-- short TTL and proper indexing.

CREATE TABLE IF NOT EXISTS intents (
    intent_id       TEXT PRIMARY KEY,
    user_id_hash    TEXT NOT NULL,
    text            TEXT NOT NULL,
    location_coarse TEXT NOT NULL, -- e.g. geohash or rounded lat/lon
    location_exact  BYTEA,         -- encrypted blob, NULL unless user consented
    radius_m        INTEGER NOT NULL,
    max_walk_minutes INTEGER NOT NULL,
    consent         JSONB NOT NULL,
    expires_at      TIMESTAMP WITH TIME ZONE NOT NULL,
    is_broadcast    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- If you already have an intents table, the minimal ALTER would be:
-- ALTER TABLE intents
--   ADD COLUMN consent JSONB,
--   ADD COLUMN user_id_hash TEXT,
--   ADD COLUMN location_coarse TEXT,
--   ADD COLUMN location_exact BYTEA,
--   ADD COLUMN expires_at TIMESTAMP WITH TIME ZONE,
--   ADD COLUMN is_broadcast BOOLEAN DEFAULT FALSE;

