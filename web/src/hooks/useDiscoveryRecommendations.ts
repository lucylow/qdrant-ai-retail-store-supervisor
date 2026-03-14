/**
 * Discovery API recommendations (RetailRocket + Qdrant).
 * POST /demo/discovery-recs with item_ids and context (co_purchased | co_carted | co_viewed).
 */

import { useCallback, useState } from "react";

const DISCOVERY_BASE =
  (import.meta.env.VITE_DISCOVERY_URL as string) || "http://localhost:8002";

export type DiscoveryRec = {
  itemid: number;
  title: string;
  score: number;
  conversion_rate: number;
  context: string;
};

export type DiscoveryRecResponse = {
  input_items: number[];
  context: string;
  recommendations: DiscoveryRec[];
  avg_score: number;
  high_conv_items: number;
  retailrocket_source?: string;
  discovery_api?: string;
  error?: string;
};

export function useDiscoveryRecommendations() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const recommend = useCallback(
    async (
      itemIds: number[],
      context: "co_purchased" | "co_carted" | "co_viewed" = "co_purchased"
    ): Promise<DiscoveryRecResponse> => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${DISCOVERY_BASE}/demo/discovery-recs`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_ids: itemIds, context }),
          signal: AbortSignal.timeout(10000),
        });
        if (!res.ok) throw new Error(`${res.status}`);
        const data = (await res.json()) as DiscoveryRecResponse;
        return data;
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Discovery request failed";
        setError(msg);
        return {
          input_items: itemIds,
          context,
          recommendations: [],
          avg_score: 0,
          high_conv_items: 0,
          error: msg,
        };
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return { recommend, loading, error };
}
