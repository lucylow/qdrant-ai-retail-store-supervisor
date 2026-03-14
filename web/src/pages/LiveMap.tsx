import { useEffect, useState } from "react";
import { MapPin, Navigation, Clock, Package } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";

type Intent = {
  intent_id: string;
  user_text: string;
  lat: number;
  lng: number;
  status: string;
};

const MOCK_INTENTS: Intent[] = [
  { intent_id: "i1", user_text: "Bio-Milch morgen 10h Zürich HB", lat: 47.3769, lng: 8.5417, status: "open" },
  { intent_id: "i2", user_text: "Raclette cheese pickup Bern", lat: 46.9480, lng: 7.4474, status: "fulfilled" },
  { intent_id: "i3", user_text: "Fondue set delivery Basel", lat: 47.5596, lng: 7.5886, status: "pending" },
  { intent_id: "i4", user_text: "Ski gear Zermatt express", lat: 46.0207, lng: 7.7491, status: "open" },
];

const STATUS_COLORS: Record<string, string> = {
  open: "bg-status-online/10 text-status-online border-status-online/30",
  pending: "bg-status-warning/10 text-status-warning border-status-warning/30",
  fulfilled: "bg-primary/10 text-primary border-primary/30",
};

export default function LiveMap() {
  const [intents, setIntents] = useState<Intent[]>(MOCK_INTENTS);
  const [query, setQuery] = useState("");

  const filtered = query
    ? intents.filter((i) => i.user_text.toLowerCase().includes(query.toLowerCase()))
    : intents;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Navigation className="w-7 h-7 text-primary" />
          Live Store Map
        </h1>
        <p className="text-muted-foreground mt-1">
          Real-time intent tracking across Swiss retail locations.
        </p>
      </div>

      <div className="flex gap-3">
        <Input
          placeholder="Filter intents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="max-w-sm"
        />
        <Button variant="outline" onClick={() => setQuery("")}>Clear</Button>
      </div>

      {/* Map placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-primary" />
            Swiss Retail Locations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-muted/50 rounded-lg p-12 text-center min-h-[350px] flex flex-col items-center justify-center gap-4">
            <MapPin className="w-16 h-16 text-muted-foreground/30" />
            <p className="text-muted-foreground">
              Interactive map visualization — showing {filtered.length} active intents across Switzerland
            </p>
            <div className="flex gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-status-online" /> Open</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-status-warning" /> Pending</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary" /> Fulfilled</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Intent list */}
      <div className="grid md:grid-cols-2 gap-4">
        {filtered.map((intent) => (
          <Card key={intent.intent_id} className="hover:border-primary/30 transition-colors">
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{intent.user_text}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {intent.lat.toFixed(4)}, {intent.lng.toFixed(4)}
                  </p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full border ${STATUS_COLORS[intent.status] || ""}`}>
                  {intent.status}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
