import { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";

type Intent = {
  intent_id: string;
  user_id: string;
  text: string;
  lat: number;
  lon: number;
  radius_m: number;
  max_walk_minutes: number;
  created_at: string;
};

type Candidate = {
  provider_id: string;
  name: string;
  lat: number;
  lon: number;
  rating: number;
  utilization: number;
  distance_m: number;
  eta_minutes: number;
  total_score: number;
};

type CandidatesResponse = {
  intent: Intent;
  candidates: Candidate[];
};

const DEFAULT_CENTER: [number, number] = [47.378, 8.54]; // Zurich HB

export function LiveMapPage() {
  const [query, setQuery] = useState("Need a haircut at 16:00 near Zurich HB");
  const [intent, setIntent] = useState<Intent | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const center: [number, number] =
    intent != null ? [intent.lat, intent.lon] : DEFAULT_CENTER;

  async function createIntent() {
    setLoading(true);
    setError(null);
    setCandidates([]);
    try {
      const resp = await fetch("/livemap/intent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "demo_user",
          text: query,
          lat: center[0],
          lon: center[1],
          radius_m: 1500,
          max_walk_minutes: 20,
        }),
      });
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const data: Intent = await resp.json();
      setIntent(data);
      await loadCandidates(data.intent_id);
    } catch (e: any) {
      setError(e?.message ?? "Failed to create intent");
    } finally {
      setLoading(false);
    }
  }

  async function loadCandidates(intentId: string) {
    try {
      const resp = await fetch(`/livemap/intent/${intentId}/candidates`);
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const data: CandidatesResponse = await resp.json();
      setCandidates(data.candidates);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load candidates");
    }
  }

  useEffect(() => {
    if (intent) {
      loadCandidates(intent.intent_id).catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex flex-col gap-4 p-4 h-full">
      <div className="grid grid-cols-1 md:grid-cols-[2fr,1fr] gap-4 h-full">
        <Card className="h-[480px] md:h-full">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>LiveMap – Geo + Semantic Matching</CardTitle>
          </CardHeader>
          <CardContent className="h-[420px] md:h-[calc(100%-4rem)] p-0">
            <MapContainer
              center={center}
              zoom={15}
              scrollWheelZoom={true}
              className="w-full h-full rounded-b-lg"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={center}>
                <Popup>Intent origin</Popup>
              </Marker>
              {candidates.map((c) => (
                <Marker key={c.provider_id} position={[c.lat, c.lon]}>
                  <Popup>
                    <div className="space-y-1">
                      <div className="font-semibold">{c.name}</div>
                      <div className="text-xs text-muted-foreground">
                        Rating {c.rating.toFixed(1)} · ETA {c.eta_minutes} min
                      </div>
                      <div className="text-xs">
                        Distance {(c.distance_m / 1000).toFixed(2)} km
                      </div>
                      <div className="text-xs">
                        Score {c.total_score.toFixed(3)}
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </CardContent>
        </Card>

        <Card className="h-full">
          <CardHeader>
            <CardTitle>Broadcast intent</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe what you need nearby..."
            />
            <Button onClick={createIntent} disabled={loading}>
              {loading ? "Matching..." : "Find nearby providers"}
            </Button>
            {error && <p className="text-sm text-red-500">{error}</p>}
            {intent && (
              <div className="text-xs text-muted-foreground space-y-1">
                <div>Intent ID: {intent.intent_id}</div>
                <div>
                  Candidates:{" "}
                  {candidates.length === 0
                    ? "none yet"
                    : `${candidates.length} providers`}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default LiveMapPage;

