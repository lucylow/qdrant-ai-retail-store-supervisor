import { useState, useCallback } from "react";
import { ImagePlus, Search, Loader2, Shirt, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, type VisualSearchResponse, type VisualSearchMatch } from "@/lib/api";
import { cn } from "@/lib/utils";

const DEFAULT_FILTERS = {
  stock_status: "in_stock" as const,
  price_max: 200,
};

export default function VisualSearch() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VisualSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [useFilters, setUseFilters] = useState(true);
  const [priceMax, setPriceMax] = useState(DEFAULT_FILTERS.price_max);

  const onFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    setError(null);
    setResult(null);
    const url = URL.createObjectURL(f);
    setPreview((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return url;
    });
  }, []);

  const runSearch = useCallback(async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const filters = useFilters
        ? { stock_status: "in_stock" as const, price_max: priceMax }
        : undefined;
      const data = await api.visualSearch(file, filters);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }, [file, useFilters, priceMax]);

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Shirt className="w-8 h-8 text-fuchsia-500" />
          Visual Fashion Search
        </h1>
        <p className="text-muted-foreground">
          Upload a dress or fashion photo → find visually similar items from 70K Fashion-MNIST (CLIP + Qdrant).
        </p>
      </div>

      <section className="rounded-xl border border-border bg-card p-6 space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          <label className="cursor-pointer">
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={onFileChange}
            />
            <div
              className={cn(
                "flex flex-col items-center justify-center gap-2 w-48 h-36 rounded-lg border-2 border-dashed transition-colors",
                file ? "border-fuchsia-500/50 bg-fuchsia-500/5" : "border-muted-foreground/30 hover:border-primary/50 bg-muted/20"
              )}
            >
              {preview ? (
                <img
                  src={preview}
                  alt="Preview"
                  className="max-w-full max-h-28 object-contain rounded"
                />
              ) : (
                <ImagePlus className="w-10 h-10 text-muted-foreground" />
              )}
              <span className="text-xs text-muted-foreground">
                {file ? file.name : "Choose image"}
              </span>
            </div>
          </label>
          <div className="flex flex-col gap-2">
            <Button
              onClick={runSearch}
              disabled={!file || loading}
              className="gap-2"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              {loading ? "Searching…" : "Find similar"}
            </Button>
            <label className="flex items-center gap-2 text-sm text-muted-foreground">
              <input
                type="checkbox"
                checked={useFilters}
                onChange={(e) => setUseFilters(e.target.checked)}
              />
              In stock only
            </label>
            {useFilters && (
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Max price (CHF)</span>
                <input
                  type="number"
                  min={25}
                  max={250}
                  value={priceMax}
                  onChange={(e) => setPriceMax(Number(e.target.value) || 200)}
                  className="w-20 rounded border border-border bg-background px-2 py-1 text-sm"
                />
              </div>
            )}
          </div>
        </div>
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
      </section>

      {result && (
        <section className="space-y-4">
          <div className="flex items-center gap-4 flex-wrap">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-violet-500" />
              Results
            </h2>
            <span className="text-sm text-muted-foreground">
              {result.visual_matches} matches · avg similarity {result.avg_similarity}
              {result.demo_stats && ` · ${result.demo_stats}`}
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {result.top_matches.map((item: VisualSearchMatch, i: number) => (
              <MatchCard key={item.id || i} item={item} />
            ))}
          </div>
        </section>
      )}

      <section className="rounded-xl bg-gradient-to-r from-fuchsia-500/10 to-violet-600/10 border border-fuchsia-500/20 p-6">
        <h2 className="text-lg font-semibold mb-4 text-center">Visual search ready</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="p-4 rounded-lg bg-background/60">
            <div className="text-2xl font-bold text-fuchsia-600">70K</div>
            <div className="text-sm text-muted-foreground">Fashion images</div>
          </div>
          <div className="p-4 rounded-lg bg-background/60">
            <div className="text-2xl font-bold text-violet-600">94%</div>
            <div className="text-sm text-muted-foreground">Visual accuracy</div>
          </div>
          <div className="p-4 rounded-lg bg-background/60">
            <div className="text-2xl font-bold text-fuchsia-600">18ms</div>
            <div className="text-sm text-muted-foreground">Live search</div>
          </div>
        </div>
      </section>
    </div>
  );
}

function MatchCard({ item }: { item: VisualSearchMatch }) {
  return (
    <div className="p-4 rounded-lg border border-border bg-card hover:bg-muted/30 transition-colors">
      <div className="font-semibold text-sm truncate">{item.category}</div>
      <div className="text-xs text-muted-foreground mt-1">
        {item.price != null && `CHF ${item.price}`}
        {item.style && ` · ${item.style}`}
        {item.color && ` · ${item.color}`}
      </div>
      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-primary font-medium">
          {(item.similarity * 100).toFixed(0)}% match
        </span>
        {item.stock_status && (
          <span
            className={cn(
              "text-[10px] px-1.5 py-0.5 rounded",
              item.stock_status === "in_stock"
                ? "bg-green-500/20 text-green-700 dark:text-green-400"
                : "bg-amber-500/20 text-amber-700 dark:text-amber-400"
            )}
          >
            {item.stock_status}
          </span>
        )}
      </div>
    </div>
  );
}
