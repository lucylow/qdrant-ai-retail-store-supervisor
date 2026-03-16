-- Geospatial mapping, navigation & logistics (Migros / Swiss retail stores)
-- Run after 001_create_livemap_tables.sql if using same DB; PostGIS already created there.
-- For standalone livemap DB: create DB then run this file (PostGIS created here).
CREATE EXTENSION IF NOT EXISTS postgis;

-- Stores table (Migros / Coop / etc. retail store locations) — tenant-scoped
CREATE TABLE IF NOT EXISTS stores (
  store_id         TEXT NOT NULL,
  tenant_id        TEXT NOT NULL DEFAULT 'migros',
  name             TEXT NOT NULL,
  address          TEXT,
  city             TEXT,
  postcode         TEXT,
  lat              DOUBLE PRECISION NOT NULL,
  lon              DOUBLE PRECISION NOT NULL,
  geom             geography(Point, 4326) NOT NULL,
  categories       TEXT[],                    -- e.g. ['supermarket','bakery']
  capabilities_text TEXT,
  opening_hours    JSONB,
  capacity         INTEGER DEFAULT 100,
  metadata         JSONB,
  created_at       TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (store_id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_stores_geom ON stores USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_stores_tenant ON stores (tenant_id);
CREATE INDEX IF NOT EXISTS idx_stores_city ON stores (tenant_id, city);

-- Inventory per store (for logistics / restock planning)
CREATE TABLE IF NOT EXISTS inventory (
  inventory_id   TEXT PRIMARY KEY,
  tenant_id      TEXT NOT NULL DEFAULT 'migros',
  store_id       TEXT NOT NULL,
  sku            TEXT,
  sku_name       TEXT,
  quantity       INTEGER,
  last_updated   TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT fk_inventory_store FOREIGN KEY (store_id, tenant_id) REFERENCES stores(store_id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_inventory_store ON inventory (store_id, tenant_id);

-- Shipments (planned / in-flight)
CREATE TABLE IF NOT EXISTS shipments (
  shipment_id   TEXT PRIMARY KEY,
  tenant_id     TEXT NOT NULL DEFAULT 'migros',
  store_id      TEXT NOT NULL,
  vehicle_id    TEXT,
  status        TEXT,   -- pending | dispatched | in_transit | completed | cancelled
  items         JSONB,
  pickup_ts     TIMESTAMPTZ,
  eta_ts        TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT fk_shipments_store FOREIGN KEY (store_id, tenant_id) REFERENCES stores(store_id, tenant_id)
);

CREATE INDEX IF NOT EXISTS idx_shipments_store ON shipments (store_id, tenant_id);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments (status);

-- Vehicle routes / assignments
CREATE TABLE IF NOT EXISTS vehicle_routes (
  route_id        TEXT PRIMARY KEY,
  tenant_id       TEXT NOT NULL DEFAULT 'migros',
  vehicle_id      TEXT,
  route_order     JSONB,   -- ordered list of stops [{store_id, eta_ts, arrival_window}]
  capacity_total  INTEGER,
  capacity_used   INTEGER DEFAULT 0,
  created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vehicle_routes_tenant ON vehicle_routes (tenant_id);
