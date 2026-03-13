import { useCallback, useEffect, useState } from "react";
import { MapPin, Truck, Clock, AlertTriangle } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export type Store = {
  store_id: string;
  name: string;
  lat: number;
  lng: number;
  canton: string;
};

type Route = {
  route_id: string;
  store_ids: string[];
  eta_minutes: number;
  distance_km: number;
};

type Props = {
  stores?: Store[];
  routes?: Route[];
  onStoreClick?: (store: Store) => void;
};

export default function MapLogistics({ stores = [], routes = [], onStoreClick }: Props) {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
        <MapPin className="w-5 h-5 text-primary" />
        Swiss Logistics Map
      </h3>
      <div className="bg-muted/50 rounded-lg p-8 text-center min-h-[400px] flex flex-col items-center justify-center gap-4">
        <Truck className="w-12 h-12 text-muted-foreground/50" />
        <p className="text-muted-foreground text-sm">
          Interactive map requires Leaflet. Showing {stores.length} stores and {routes.length} routes.
        </p>
        {stores.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-4 w-full max-w-lg">
            {stores.slice(0, 6).map((store) => (
              <button
                key={store.store_id}
                onClick={() => onStoreClick?.(store)}
                className="text-xs p-2 rounded-lg border border-border bg-background hover:border-primary/30 transition-colors text-left"
              >
                <div className="font-medium truncate">{store.name}</div>
                <div className="text-muted-foreground">{store.canton}</div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
