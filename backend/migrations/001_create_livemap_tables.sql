-- LiveMap core relational schemas (Postgres + PostGIS).
-- This migration is tenant-aware and privacy-by-design.

CREATE EXTENSION IF NOT EXISTS postgis;

-- USERS (pseudonymized id, minimal PII)
CREATE TABLE IF NOT EXISTS users (
  user_id_hash TEXT PRIMARY KEY,           -- pseudonymized HMAC
  tenant_id    TEXT NOT NULL,              -- retailer tenant (e.g. 'coop', 'migros')
  created_at   TIMESTAMPTZ DEFAULT now(),
  prefs        JSONB,
  consent      JSONB,
  metadata     JSONB
);

-- PROVIDERS (merchants / locations)
CREATE TABLE IF NOT EXISTS providers (
  provider_id        TEXT PRIMARY KEY,
  tenant_id          TEXT NOT NULL,
  name               TEXT,
  business_name      TEXT,
  address            TEXT,
  lat                DOUBLE PRECISION,
  lon                DOUBLE PRECISION,
  geom               geography(Point,4326),
  categories         TEXT[],
  capabilities_text  TEXT,
  rating             DOUBLE PRECISION,
  price_min_cents    INTEGER,
  price_max_cents    INTEGER,
  metadata           JSONB,
  created_at         TIMESTAMPTZ DEFAULT now()
);

-- AVAILABILITY SLOTS (provider capacity / calendar)
CREATE TABLE IF NOT EXISTS availability_slots (
  slot_id    TEXT PRIMARY KEY,
  tenant_id  TEXT NOT NULL,
  provider_id TEXT NOT NULL REFERENCES providers(provider_id),
  start_ts   TIMESTAMPTZ NOT NULL,
  end_ts     TIMESTAMPTZ NOT NULL,
  capacity   INTEGER DEFAULT 1,
  metadata   JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- INTENTS (ephemeral user broadcast)
CREATE TABLE IF NOT EXISTS intents (
  intent_id        TEXT PRIMARY KEY,
  tenant_id        TEXT NOT NULL,
  user_id_hash     TEXT REFERENCES users(user_id_hash),
  raw_text         TEXT,
  structured       JSONB,
  lat              DOUBLE PRECISION,
  lon              DOUBLE PRECISION,
  location_coarse  TEXT,
  location_exact   BYTEA,
  geom             geography(Point,4326),
  radius_m         INTEGER DEFAULT 1500,
  status           TEXT DEFAULT 'broadcasting',
  is_broadcast     BOOLEAN DEFAULT TRUE,
  consent          JSONB,
  expires_at       TIMESTAMPTZ,
  created_at       TIMESTAMPTZ DEFAULT now()
);

-- BIDS / OFFERS by providers in response to an intent
CREATE TABLE IF NOT EXISTS bids (
  bid_id      TEXT PRIMARY KEY,
  tenant_id   TEXT NOT NULL,
  intent_id   TEXT NOT NULL REFERENCES intents(intent_id),
  provider_id TEXT NOT NULL REFERENCES providers(provider_id),
  price_cents INTEGER,
  eta_minutes INTEGER,
  expires_at  TIMESTAMPTZ,
  payload     JSONB,
  created_at  TIMESTAMPTZ DEFAULT now(),
  status      TEXT DEFAULT 'open'   -- open|accepted|rejected|expired
);

-- BOOKINGS (confirmed matches)
CREATE TABLE IF NOT EXISTS bookings (
  booking_id  TEXT PRIMARY KEY,
  tenant_id   TEXT NOT NULL,
  intent_id   TEXT NOT NULL REFERENCES intents(intent_id),
  bid_id      TEXT REFERENCES bids(bid_id),
  provider_id TEXT NOT NULL REFERENCES providers(provider_id),
  user_id_hash TEXT REFERENCES users(user_id_hash),
  start_ts    TIMESTAMPTZ,
  end_ts      TIMESTAMPTZ,
  status      TEXT DEFAULT 'scheduled',  -- scheduled|completed|cancelled
  metadata    JSONB,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- EPISODES (logged outcomes for learning / AutoRAG)
CREATE TABLE IF NOT EXISTS episodes (
  episode_id      TEXT PRIMARY KEY,
  tenant_id       TEXT NOT NULL,
  intent_id       TEXT REFERENCES intents(intent_id),
  booking_id      TEXT REFERENCES bookings(booking_id),
  provider_id     TEXT,
  user_id_hash    TEXT,
  intent_summary  TEXT,
  provider_summary TEXT,
  outcome         JSONB,
  created_at      TIMESTAMPTZ DEFAULT now()
);

-- AUX: deletion requests (for GDPR / Swiss data subject rights)
CREATE TABLE IF NOT EXISTS deletion_requests (
  request_id   TEXT PRIMARY KEY,
  tenant_id    TEXT NOT NULL,
  user_id_hash TEXT,
  requested_at TIMESTAMPTZ DEFAULT now(),
  completed_at TIMESTAMPTZ,
  status       TEXT DEFAULT 'pending',
  metadata     JSONB
);

-- Index suggestions
CREATE INDEX IF NOT EXISTS idx_providers_geog
  ON providers USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_providers_tenant
  ON providers (tenant_id);

CREATE INDEX IF NOT EXISTS idx_intents_geog
  ON intents USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_intents_expires_at
  ON intents (expires_at);

CREATE INDEX IF NOT EXISTS idx_intents_status
  ON intents (status);

CREATE INDEX IF NOT EXISTS idx_intents_tenant
  ON intents (tenant_id);

CREATE INDEX IF NOT EXISTS idx_bids_intent
  ON bids (intent_id);

CREATE INDEX IF NOT EXISTS idx_bids_tenant
  ON bids (tenant_id);

CREATE INDEX IF NOT EXISTS idx_bookings_tenant
  ON bookings (tenant_id);

CREATE INDEX IF NOT EXISTS idx_availability_provider
  ON availability_slots (provider_id);

CREATE INDEX IF NOT EXISTS idx_availability_tenant
  ON availability_slots (tenant_id);

