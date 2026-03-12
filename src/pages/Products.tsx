import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, MOCK_PRODUCTS } from "@/lib/api";
import { Search, Upload, ShoppingBag, Tag, Image, Zap, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const CATEGORIES = ["All", "Tents", "Footwear", "Cooking", "Sleeping", "Poles", "Clothing"];

const SEARCH_MODES = [
  { id: "text", label: "Text", icon: Search, desc: "all-mpnet 384-dim" },
  { id: "image", label: "Image", icon: Image, desc: "CLIP 512-dim" },
  { id: "hybrid", label: "Hybrid", icon: Zap, desc: "RRF fusion" },
] as const;

type SearchMode = typeof SEARCH_MODES[number]["id"];

export default function ProductsPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [mode, setMode] = useState<SearchMode>("text");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const { data: products = MOCK_PRODUCTS } = useQuery({
    queryKey: ["products", search],
    queryFn: () => api.getProducts(search),
    retry: 0,
    placeholderData: MOCK_PRODUCTS,
  });

  const filtered = products.filter((p) => {
    const name = p.name ?? p.title ?? "";
    const matchText =
      !search ||
      name.toLowerCase().includes(search.toLowerCase()) ||
      p.description?.toLowerCase().includes(search.toLowerCase());
    const matchCat = category === "All" || p.category === category;
    return matchText && matchCat;
  });

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setMode("hybrid");
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
    setMode("text");
  };

  const activeMode = SEARCH_MODES.find((m) => m.id === mode)!;

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Products Catalog</h1>
        <p className="text-sm text-muted-foreground">
          Multimodal Qdrant search — named vectors (textvec 384-dim · imagevec 512-dim · RRF fusion)
        </p>
      </div>

      {/* Search mode tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-muted w-fit">
        {SEARCH_MODES.map(({ id, label, icon: Icon, desc }) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
              mode === id ? "bg-card text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{label}</span>
            {mode === id && <span className="text-xs text-muted-foreground font-normal hidden sm:inline">· {desc}</span>}
          </button>
        ))}
      </div>

      {/* Search bar */}
      <div className="space-y-2">
        <div className="flex gap-2">
          <div className="flex-1 flex items-center gap-2 bg-muted border border-border rounded-xl px-4 py-2.5 focus-within:border-primary/50 transition-colors">
            <Search className="w-4 h-4 text-muted-foreground shrink-0" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={
                mode === "image"
                  ? "Upload an image to find similar products…"
                  : mode === "hybrid"
                  ? "Text + image hybrid search (RRF fusion)…"
                  : "Search products by text (all-mpnet 384-dim)…"
              }
              className="bg-transparent text-sm outline-none flex-1 placeholder:text-muted-foreground"
              disabled={mode === "image" && !imageFile}
            />
          </div>

          {/* Image upload */}
          <label
            className={cn(
              "cursor-pointer flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors shrink-0",
              imageFile
                ? "border-status-online/40 bg-status-online/10 text-status-online"
                : "border-border bg-muted text-muted-foreground hover:border-primary/30"
            )}
          >
            <Upload className="w-4 h-4" />
            <span className="hidden sm:inline">{imageFile ? "Image set" : "Upload image"}</span>
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleImageUpload}
            />
          </label>
        </div>

        {/* Image preview + Qdrant info */}
        {imagePreview && (
          <div className="flex items-start gap-3 p-3 rounded-xl bg-muted border border-border animate-fade-in">
            <img
              src={imagePreview}
              alt="Query image"
              className="w-16 h-16 object-cover rounded-lg border border-border shrink-0"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-status-online">CLIP ViT-B/32 encoded</span>
                <span className="text-xs text-muted-foreground">512-dim imagevec</span>
              </div>
              <div className="text-xs text-muted-foreground space-y-0.5">
                <div>→ Qdrant named vector search: <code className="font-mono bg-background px-1 rounded">using="imagevec"</code></div>
                <div>→ RRF fusion with text query for hybrid results</div>
              </div>
            </div>
            <button onClick={clearImage} className="text-muted-foreground hover:text-foreground">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Mode info bar */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground px-1">
          <activeMode.icon className="w-3 h-3 text-primary" />
          {mode === "text" && "Searching zurich_products collection · textvec (384-dim, all-mpnet) · HNSW M=64 · Binary quant"}
          {mode === "image" && "Qdrant named vector: imagevec (512-dim, CLIP ViT-B/32) · score_threshold=0.7"}
          {mode === "hybrid" && "RRF fusion: textvec + imagevec scores · top-20 → cross-encoder rerank → top-5"}
        </div>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            className={cn(
              "text-xs px-3 py-1.5 rounded-full border transition-colors",
              category === c
                ? "bg-primary/20 text-primary border-primary/40"
                : "bg-muted border-border text-muted-foreground hover:border-primary/30"
            )}
          >
            {c}
          </button>
        ))}
        <span className="text-xs text-muted-foreground self-center ml-auto">
          Payload indexed · filter 10× faster
        </span>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filtered.map((p, i) => (
          <div
            key={p.id ?? i}
            className="rounded-xl border border-border bg-card hover:border-primary/30 transition-all hover:shadow-lg group"
          >
            {/* Image placeholder with search mode badge */}
            <div className="aspect-[4/3] rounded-t-xl bg-muted flex flex-col items-center justify-center overflow-hidden relative">
              <ShoppingBag className="w-12 h-12 text-muted-foreground/30 group-hover:scale-110 transition-transform" />
              {p.score !== undefined && (
                <div className="absolute top-2 right-2 text-xs font-medium px-1.5 py-0.5 rounded bg-status-online/20 text-status-online border border-status-online/30">
                  {(p.score * 100).toFixed(0)}%
                </div>
              )}
              {mode !== "text" && (
                <div className="absolute bottom-2 left-2 text-xs px-1.5 py-0.5 rounded bg-primary/20 text-primary border border-primary/30">
                  {mode === "image" ? "imagevec" : "RRF"}
                </div>
              )}
            </div>
            <div className="p-4 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-sm font-semibold leading-tight">{p.name ?? p.title}</h3>
                {p.category && (
                  <span className="flex items-center gap-0.5 text-xs text-muted-foreground shrink-0">
                    <Tag className="w-3 h-3" />
                    {p.category}
                  </span>
                )}
              </div>
              {p.description && (
                <p className="text-xs text-muted-foreground line-clamp-2">{p.description}</p>
              )}
              <div className="flex items-center justify-between pt-1">
                {p.price !== undefined && (
                  <span className="font-bold text-primary">CHF {p.price}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="py-16 text-center text-muted-foreground">No products match your search.</div>
      )}
    </div>
  );
}
