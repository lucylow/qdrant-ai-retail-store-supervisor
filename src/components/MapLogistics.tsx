import { useCallback, useEffect, useState } from "react";
import {
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  Polyline,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export type Store = {
  store_id: string;
  name: string;
  address?: string;
  city?: string;
  lat: number;
  lon: number;
  categories: string[];
  capabilities_text?: string;
  capacity?: number;
};

type MapLogisticsProps = {
  center?: [number, number];
  apiBase?: string;
};

type LineStringGeom = { type: "LineString"; coordinates: number[][] } | null;

function RouteLine({ geometry }: { geometry: LineStringGeom }) {
  if (!geometry?.coordinates?.length) return null;
  const latlngs = geometry.coordinates.map(
    (c: number[]) => [c[1], c[0]] as [number, number]
  );
  return (
    <Polyline
      positions={latlngs}
      pathOptions={{ color: "#e11d48", weight: 4 }}
    />
  );
}

export function MapLogistics({
  center = [47.3769, 8.5417],
  apiBase = API_BASE,
}: MapLogisticsProps) {
  const [stores, setStores] = useState<Store[]>([]);
  const [routeGeojson, setRouteGeojson] = useState<LineStringGeom>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `${apiBase}/api/stores/nearby?lat=${center[0]}&lon=${center[1]}&radius_m=5000&limit=100`
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) setStores(data);
      } catch (e: unknown) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Failed to load stores");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [center[0], center[1], apiBase]);

  const showRouteTo = useCallback(
    async (store: Store) => {
      setError(null);
      try {
        const res = await fetch(`${apiBase}/api/routing/route`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            from_lat: center[0],
            from_lon: center[1],
            to_store_id: store.store_id,
            profile: "driving",
          }),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.routes?.[0]?.geometry) {
          setRouteGeojson(data.routes[0].geometry);
        } else {
          setRouteGeojson(null);
        }
      } catch (e: unknown) {
        setError(
          e instanceof Error ? e.message : "Routing not available (set MAPBOX_TOKEN or OSRM_URL)"
        );
        setRouteGeojson(null);
      }
    },
    [center[0], center[1], apiBase]
  );

  const defaultIcon = L.divIcon({
    html: `<div style="width:24px;height:24px;border-radius:6px;background:#0ea5a4;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold">M</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

  return (
    <div className="relative w-full h-full">
      {loading && (
        <div className="absolute top-2 left-2 z-[1000] bg-background/90 px-2 py-1 rounded text-sm">
          Loading stores…
        </div>
      )}
      {error && (
        <div className="absolute top-2 left-2 z-[1000] bg-destructive/90 text-destructive-foreground px-2 py-1 rounded text-sm max-w-xs">
          {error}
        </div>
      )}
      <MapContainer
        center={center}
        zoom={13}
        scrollWheelZoom
        className="w-full h-full rounded-lg"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={center} icon={defaultIcon}>
          <Popup>You are here</Popup>
        </Marker>
        {stores.map((s) => (
          <Marker
            key={s.store_id}
            position={[s.lat, s.lon]}
            icon={defaultIcon}
            eventHandlers={{ click: () => showRouteTo(s) }}
          >
            <Popup>
              <div className="space-y-1 min-w-[160px]">
                <div className="font-semibold">{s.name}</div>
                {s.address && (
                  <div className="text-xs text-muted-foreground">{s.address}</div>
                )}
                <button
                  type="button"
                  className="text-xs text-primary underline"
                  onClick={() => showRouteTo(s)}
                >
                  Show route
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
        <RouteLine geometry={routeGeojson} />
      </MapContainer>
    </div>
  );
}

export default MapLogistics;
