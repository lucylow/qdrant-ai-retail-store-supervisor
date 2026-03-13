import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

type RouteStop = {
  store_id: string;
  lat: number;
  lon: number;
  eta_s: number;
};

type PlannedRoute = {
  vehicle_id: string;
  route: RouteStop[];
};

type LogisticsPanelProps = {
  apiBase?: string;
  depot?: { lat: number; lon: number };
};

export function LogisticsPanel({
  apiBase = API_BASE,
  depot = { lat: 47.3769, lon: 8.5417 },
}: LogisticsPanelProps) {
  const [routes, setRoutes] = useState<PlannedRoute[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const planRoutes = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/logistics/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          depot_lat: depot.lat,
          depot_lon: depot.lon,
          vehicle_count: 2,
          capacity: 500,
          tenant_id: "migros",
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setRoutes(Array.isArray(data) ? data : []);
    } catch (e: unknown) {
      setError(
        e instanceof Error ? e.message : "Plan failed (ensure DB has stores with low inventory)"
      );
      setRoutes([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Logistics – Plan routes</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">
          Plan vehicle routes for stores needing restock (greedy VRP). Depot:{" "}
          {depot.lat.toFixed(4)}, {depot.lon.toFixed(4)}
        </p>
        <Button onClick={planRoutes} disabled={loading}>
          {loading ? "Planning…" : "Plan routes"}
        </Button>
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
        <div className="space-y-2">
          {routes.map((r) => (
            <div
              key={r.vehicle_id}
              className="border rounded-md p-3 bg-muted/30"
            >
              <div className="font-medium">{r.vehicle_id}</div>
              <ol className="list-decimal list-inside text-sm mt-1 space-y-0.5">
                {r.route.map((s) => (
                  <li key={s.store_id}>
                    {s.store_id} — ETA {Math.round(s.eta_s / 60)} min
                  </li>
                ))}
                {r.route.length === 0 && (
                  <li className="text-muted-foreground">No stops</li>
                )}
              </ol>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default LogisticsPanel;
