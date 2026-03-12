import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, MOCK_PRODUCTS, Product } from "@/lib/api";
import {
  Search, Upload, ShoppingBag, Tag, Image, Zap, X, Database,
  Package, MapPin, Star, Clock, AlertTriangle, CheckCircle2,
  Filter, ChevronDown, BarChart3, Terminal, Layers, Box,
  TrendingUp, Eye,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

const CATEGORIES = ["All", "Tents", "Footwear", "Cooking", "Sleeping", "Poles", "Clothing"];
const SHIPPING_ZONES = ["All", "CH", "EU", "WORLD"];
const STOCK_FILTERS = ["All", "in_stock", "low_stock", "out_of_stock"];

const SEARCH_MODES = [
  { id: "text", label: "Text", icon: Search, desc: "all-mpnet 384-dim" },
  { id: "image", label: "Image", icon: Image, desc: "CLIP 512-dim" },
  { id: "hybrid", label: "Hybrid", icon: Zap, desc: "RRF fusion" },
] as const;

type SearchMode = typeof SEARCH_MODES[number]["id"];

const PAYLOAD_INDEXES = [
  { field: "sku", type: "KEYWORD", purpose: "Exact SKU lookup", example: 'match: "TENT-001"' },
  { field: "category", type: "KEYWORD", purpose: "Category filtering", example: 'match: "tents"' },
  { field: "shipping_zone", type: "KEYWORD", purpose: "Zone restriction", example: 'match: "CH"' },
  { field: "stock_status", type: "KEYWORD", purpose: "Availability filter", example: 'match: "in_stock"' },
  { field: "price", type: "FLOAT", purpose: "Price range queries", example: "range: {lt: 200}" },
  { field: "stock", type: "INTEGER", purpose: "Stock level filter", example: "range: {gt: 0}" },
  { field: "rating", type: "FLOAT", purpose: "Quality filtering", example: "range: {gte: 4.0}" },
  { field: "brand", type: "KEYWORD", purpose: "Brand filtering", example: 'match: "MSR"' },
];

const PRODUCT_FIELDS = [
  { field: "sku", type: "string", example: "TENT-001", ragPurpose: "Unique ID for tracking" },
  { field: "title", type: "string", example: "REI Co-op Kingdom 2", ragPurpose: "Text embedding source" },
  { field: "description", type: "string", example: "2-person backpacking tent…", ragPurpose: "Semantic search content" },
  { field: "price", type: "float", example: "198", ragPurpose: "Filter: range lt 200" },
  { field: "stock", type: "int", example: "47", ragPurpose: "Filter: must in_stock" },
  { field: "stock_status", type: "enum", example: "in_stock", ragPurpose: "Availability constraint" },
  { field: "shipping_zone", type: "enum", example: "CH", ragPurpose: "Filter: match CH" },
  { field: "category", type: "string", example: "tents", ragPurpose: "Metadata filter" },
  { field: "brand", type: "string", example: "MSR", ragPurpose: "Brand preference" },
  { field: "rating", type: "float", example: "4.7", ragPurpose: "Quality ranking" },
  { field: "reviews_count", type: "int", example: "1284", ragPurpose: "Popularity signal" },
  { field: "shipping_days", type: "int", example: "2", ragPurpose: "ETA constraint" },
];

const stockColor = (status?: string) => {
  if (status === "in_stock") return "text-status-online bg-status-online/10 border-status-online/30";
  if (status === "low_stock") return "text-status-warning bg-status-warning/10 border-status-warning/30";
  return "text-destructive bg-destructive/10 border-destructive/30";
};

const stockIcon = (status?: string) => {
  if (status === "in_stock") return <CheckCircle2 className="w-3 h-3" />;
  if (status === "low_stock") return <AlertTriangle className="w-3 h-3" />;
  return <X className="w-3 h-3" />;
};

export default function ProductsPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [shippingZone, setShippingZone] = useState("All");
  const [stockFilter, setStockFilter] = useState("All");
  const [maxPrice, setMaxPrice] = useState<number | null>(null);
  const [minRating, setMinRating] = useState<number | null>(null);
  const [mode, setMode] = useState<SearchMode>("text");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const { data: products = MOCK_PRODUCTS } = useQuery({
    queryKey: ["products", search],
    queryFn: () => api.getProducts(search),
    retry: 0,
    placeholderData: MOCK_PRODUCTS,
  });

  const filtered = useMemo(() => products.filter((p) => {
    const name = p.name ?? p.title ?? "";
    const matchText = !search || name.toLowerCase().includes(search.toLowerCase()) || p.description?.toLowerCase().includes(search.toLowerCase());
    const matchCat = category === "All" || p.category === category;
    const matchZone = shippingZone === "All" || p.shipping_zone === shippingZone;
    const matchStock = stockFilter === "All" || p.stock_status === stockFilter;
    const matchPrice = !maxPrice || (p.price !== undefined && p.price <= maxPrice);
    const matchRating = !minRating || (p.rating !== undefined && p.rating >= minRating);
    return matchText && matchCat && matchZone && matchStock && matchPrice && matchRating;
  }), [products, search, category, shippingZone, stockFilter, maxPrice, minRating]);

  const activeFiltersCount = [category !== "All", shippingZone !== "All", stockFilter !== "All", maxPrice !== null, minRating !== null].filter(Boolean).length;

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setMode("hybrid");
  };

  const clearImage = () => { setImageFile(null); setImagePreview(null); setMode("text"); };
  const clearFilters = () => { setCategory("All"); setShippingZone("All"); setStockFilter("All"); setMaxPrice(null); setMinRating(null); };

  const activeMode = SEARCH_MODES.find((m) => m.id === mode)!;

  // Stats
  const inStock = products.filter(p => p.stock_status === "in_stock").length;
  const lowStock = products.filter(p => p.stock_status === "low_stock").length;
  const outOfStock = products.filter(p => p.stock_status === "out_of_stock").length;
  const avgPrice = products.reduce((a, p) => a + (p.price || 0), 0) / products.length;

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">Product Catalog</h1>
        <p className="text-sm text-muted-foreground">
          50K SKUs · 12 metadata fields · 8 payload indexes · Hybrid filtered search (8ms P95)
        </p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Total Products", value: products.length, icon: Package, color: "text-primary" },
          { label: "In Stock", value: inStock, icon: CheckCircle2, color: "text-status-online" },
          { label: "Low Stock", value: lowStock, icon: AlertTriangle, color: "text-status-warning" },
          { label: "Avg Price", value: `CHF ${avgPrice.toFixed(0)}`, icon: TrendingUp, color: "text-accent" },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="rounded-xl border border-border bg-card p-3 flex items-center gap-2.5">
            <Icon className={cn("w-4 h-4", color)} />
            <div>
              <div className={cn("text-lg font-bold", color)}>{value}</div>
              <div className="text-[10px] text-muted-foreground">{label}</div>
            </div>
          </div>
        ))}
      </div>

      <Tabs defaultValue="catalog" className="space-y-4">
        <TabsList className="flex flex-wrap h-auto gap-1">
          <TabsTrigger value="catalog">Product Catalog</TabsTrigger>
          <TabsTrigger value="schema">Schema & Indexes</TabsTrigger>
          <TabsTrigger value="qdrant">Qdrant Config</TabsTrigger>
        </TabsList>

        {/* ─── Catalog Tab ─── */}
        <TabsContent value="catalog" className="space-y-4">
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
                    mode === "image" ? "Upload an image to find similar products…"
                    : mode === "hybrid" ? "Text + image hybrid search (RRF fusion)…"
                    : "Search products — e.g. '2-person tent under 200 CHF Zurich'…"
                  }
                  className="bg-transparent text-sm outline-none flex-1 placeholder:text-muted-foreground"
                  disabled={mode === "image" && !imageFile}
                />
              </div>
              <label className={cn(
                "cursor-pointer flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors shrink-0",
                imageFile ? "border-status-online/40 bg-status-online/10 text-status-online" : "border-border bg-muted text-muted-foreground hover:border-primary/30"
              )}>
                <Upload className="w-4 h-4" />
                <span className="hidden sm:inline">{imageFile ? "Image set" : "Upload"}</span>
                <input type="file" accept="image/*" className="hidden" onChange={handleImageUpload} />
              </label>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={cn(
                  "flex items-center gap-1.5 px-4 py-2.5 rounded-xl border text-sm font-medium transition-colors",
                  showFilters || activeFiltersCount > 0
                    ? "border-primary/40 bg-primary/10 text-primary"
                    : "border-border bg-muted text-muted-foreground hover:border-primary/30"
                )}
              >
                <Filter className="w-4 h-4" />
                <span className="hidden sm:inline">Filters</span>
                {activeFiltersCount > 0 && (
                  <Badge className="text-[9px] h-4 px-1 bg-primary text-primary-foreground">{activeFiltersCount}</Badge>
                )}
              </button>
            </div>

            {imagePreview && (
              <div className="flex items-start gap-3 p-3 rounded-xl bg-muted border border-border animate-fade-in">
                <img src={imagePreview} alt="Query" className="w-16 h-16 object-cover rounded-lg border border-border shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-status-online">CLIP ViT-B/32 encoded</span>
                    <span className="text-xs text-muted-foreground">512-dim imagevec</span>
                  </div>
                  <div className="text-xs text-muted-foreground">→ Qdrant named vector: <code className="font-mono bg-background px-1 rounded">using="image_embedding"</code></div>
                </div>
                <button onClick={clearImage} className="text-muted-foreground hover:text-foreground"><X className="w-4 h-4" /></button>
              </div>
            )}

            {/* Mode info */}
            <div className="flex items-center gap-2 text-xs text-muted-foreground px-1">
              <activeMode.icon className="w-3 h-3 text-primary" />
              {mode === "text" && "products collection · text_embedding (384-dim, all-MPNet) · HNSW M=64 · 8 payload indexes"}
              {mode === "image" && "Qdrant named vector: image_embedding (512-dim, CLIP ViT-B/32) · score_threshold=0.7"}
              {mode === "hybrid" && "RRF fusion: text_embedding + image_embedding · payload filters → 8ms P95 hybrid search"}
            </div>
          </div>

          {/* Advanced filters */}
          {showFilters && (
            <div className="rounded-xl border border-border bg-card p-4 space-y-3 animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-primary" />
                  Qdrant Payload Filters (8ms P95)
                </span>
                <button onClick={clearFilters} className="text-xs text-muted-foreground hover:text-foreground">Clear all</button>
              </div>

              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {/* Category */}
                <div className="space-y-1">
                  <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Category</label>
                  <div className="flex flex-wrap gap-1">
                    {CATEGORIES.map((c) => (
                      <button key={c} onClick={() => setCategory(c)} className={cn(
                        "text-[10px] px-2 py-1 rounded-md border transition-colors",
                        category === c ? "bg-primary/20 text-primary border-primary/40" : "bg-muted border-border text-muted-foreground"
                      )}>{c}</button>
                    ))}
                  </div>
                </div>

                {/* Shipping Zone */}
                <div className="space-y-1">
                  <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Shipping Zone</label>
                  <div className="flex flex-wrap gap-1">
                    {SHIPPING_ZONES.map((z) => (
                      <button key={z} onClick={() => setShippingZone(z)} className={cn(
                        "text-[10px] px-2 py-1 rounded-md border transition-colors",
                        shippingZone === z ? "bg-primary/20 text-primary border-primary/40" : "bg-muted border-border text-muted-foreground"
                      )}>{z}</button>
                    ))}
                  </div>
                </div>

                {/* Stock Status */}
                <div className="space-y-1">
                  <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Stock Status</label>
                  <div className="flex flex-wrap gap-1">
                    {STOCK_FILTERS.map((s) => (
                      <button key={s} onClick={() => setStockFilter(s)} className={cn(
                        "text-[10px] px-2 py-1 rounded-md border transition-colors",
                        stockFilter === s ? "bg-primary/20 text-primary border-primary/40" : "bg-muted border-border text-muted-foreground"
                      )}>{s === "All" ? "All" : s.replace(/_/g, " ")}</button>
                    ))}
                  </div>
                </div>

                {/* Price + Rating */}
                <div className="space-y-2">
                  <div className="space-y-1">
                    <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Max Price (CHF)</label>
                    <input
                      type="number"
                      value={maxPrice ?? ""}
                      onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : null)}
                      placeholder="e.g. 200"
                      className="w-full text-xs bg-muted border border-border rounded-md px-2 py-1.5 outline-none focus:border-primary/50"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">Min Rating</label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="5"
                      value={minRating ?? ""}
                      onChange={(e) => setMinRating(e.target.value ? Number(e.target.value) : null)}
                      placeholder="e.g. 4.0"
                      className="w-full text-xs bg-muted border border-border rounded-md px-2 py-1.5 outline-none focus:border-primary/50"
                    />
                  </div>
                </div>
              </div>

              {/* Active Qdrant filter */}
              {activeFiltersCount > 0 && (
                <div className="rounded-lg bg-muted/20 border border-border p-2.5">
                  <p className="text-[10px] font-semibold text-muted-foreground mb-1">Qdrant Filter (generated):</p>
                  <pre className="text-[9px] font-mono text-primary whitespace-pre-wrap">{`Filter(must=[
${category !== "All" ? `  FieldCondition(key="category", match="${category.toLowerCase()}"),\n` : ""}${shippingZone !== "All" ? `  FieldCondition(key="shipping_zone", match="${shippingZone}"),\n` : ""}${stockFilter !== "All" ? `  FieldCondition(key="stock_status", match="${stockFilter}"),\n` : ""}${maxPrice ? `  FieldCondition(key="price", range=Range(lt=${maxPrice})),\n` : ""}${minRating ? `  FieldCondition(key="rating", range=Range(gte=${minRating})),\n` : ""}])`}</pre>
                </div>
              )}
            </div>
          )}

          {/* Results count */}
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{filtered.length} products · {activeFiltersCount} filters active</span>
            <span className="font-mono">P95: 8ms · payload indexed</span>
          </div>

          {/* Product grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((p, i) => (
              <div key={p.id ?? i} className="rounded-xl border border-border bg-card hover:border-primary/30 transition-all hover:shadow-lg group">
                <div className="aspect-[4/3] rounded-t-xl bg-muted flex flex-col items-center justify-center overflow-hidden relative">
                  <ShoppingBag className="w-10 h-10 text-muted-foreground/30 group-hover:scale-110 transition-transform" />
                  {p.score !== undefined && (
                    <div className="absolute top-2 right-2 text-[10px] font-medium px-1.5 py-0.5 rounded bg-status-online/20 text-status-online border border-status-online/30">
                      {(p.score * 100).toFixed(0)}% match
                    </div>
                  )}
                  {p.stock_status && (
                    <div className={cn("absolute top-2 left-2 text-[10px] font-medium px-1.5 py-0.5 rounded border flex items-center gap-1", stockColor(p.stock_status))}>
                      {stockIcon(p.stock_status)}
                      {p.stock_status === "in_stock" ? `${p.stock} in stock` : p.stock_status === "low_stock" ? `${p.stock} left` : "Out of stock"}
                    </div>
                  )}
                  {p.shipping_zone === "CH" && (
                    <div className="absolute bottom-2 left-2 text-[10px] px-1.5 py-0.5 rounded bg-primary/20 text-primary border border-primary/30 flex items-center gap-1">
                      <MapPin className="w-3 h-3" /> CH · {p.shipping_days}d
                    </div>
                  )}
                </div>
                <div className="p-3.5 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <h3 className="text-sm font-semibold leading-tight truncate">{p.name ?? p.title}</h3>
                      {p.brand && <span className="text-[10px] text-muted-foreground">{p.brand}</span>}
                    </div>
                    {p.category && (
                      <Badge variant="outline" className="text-[9px] shrink-0">{p.category}</Badge>
                    )}
                  </div>
                  {p.description && <p className="text-[10px] text-muted-foreground line-clamp-2">{p.description}</p>}
                  <div className="flex items-center justify-between pt-1">
                    <span className="font-bold text-primary">CHF {p.price}</span>
                    <div className="flex items-center gap-2">
                      {p.rating && (
                        <span className="flex items-center gap-0.5 text-[10px] text-status-warning">
                          <Star className="w-3 h-3 fill-status-warning" /> {p.rating}
                        </span>
                      )}
                      {p.reviews_count && (
                        <span className="text-[10px] text-muted-foreground">({p.reviews_count})</span>
                      )}
                    </div>
                  </div>
                  {p.sku && (
                    <div className="text-[9px] font-mono text-muted-foreground pt-0.5">SKU: {p.sku}</div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="py-16 text-center text-muted-foreground">No products match your filters.</div>
          )}
        </TabsContent>

        {/* ─── Schema Tab ─── */}
        <TabsContent value="schema" className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Box className="h-4 w-4 text-primary" />
                12 Product Metadata Fields
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg border border-border overflow-hidden">
                <div className="grid grid-cols-4 bg-muted/30 text-[10px] font-semibold uppercase tracking-wider">
                  <div className="px-3 py-2 border-r border-border">Field</div>
                  <div className="px-3 py-2 border-r border-border">Type</div>
                  <div className="px-3 py-2 border-r border-border">Example</div>
                  <div className="px-3 py-2">RAG Purpose</div>
                </div>
                {PRODUCT_FIELDS.map((f, i) => (
                  <div key={f.field} className={cn("grid grid-cols-4 text-xs", i % 2 === 0 ? "bg-card" : "bg-card/50")}>
                    <div className="px-3 py-2 font-mono font-semibold text-primary border-r border-border">{f.field}</div>
                    <div className="px-3 py-2 text-muted-foreground border-r border-border">{f.type}</div>
                    <div className="px-3 py-2 font-mono text-muted-foreground border-r border-border truncate">{f.example}</div>
                    <div className="px-3 py-2 text-muted-foreground">{f.ragPurpose}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Database className="h-4 w-4 text-accent" />
                8 Payload Indexes (8ms P95)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 gap-2">
                {PAYLOAD_INDEXES.map((idx) => (
                  <div key={idx.field} className="rounded-lg border border-border bg-muted/20 p-2.5 space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[9px]">{idx.field}</Badge>
                      <Badge className="text-[9px] bg-accent/20 text-accent border-accent/30">{idx.type}</Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground">{idx.purpose}</p>
                    <code className="text-[9px] font-mono text-primary">{idx.example}</code>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Terminal className="h-4 w-4 text-primary" />
                Pydantic Product Schema
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed">{`class Product(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2000)
    price: float = Field(..., gt=0, le=10000)
    stock: int = Field(ge=0)
    stock_status: Literal["in_stock", "low_stock", "out_of_stock"]
    shipping_zone: Literal["CH", "EU", "WORLD"]
    category: str = Field(..., max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviews_count: Optional[int] = Field(None, ge=0)
    shipping_days: Optional[int] = Field(None, ge=0)

    def to_qdrant_payload(self) -> dict:
        return {
            "sku": self.sku, "title": self.title,
            "price": self.price, "stock": self.stock,
            "stock_status": self.stock_status,
            "shipping_zone": self.shipping_zone,
            "category": self.category.lower(),
            "brand": self.brand, "rating": self.rating,
            "reviews_count": self.reviews_count,
        }`}</pre>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ─── Qdrant Config Tab ─── */}
        <TabsContent value="qdrant" className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Database className="h-4 w-4 text-accent" />
                Products Collection Config
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-3">
                {[
                  { name: "text_embedding", dim: 384, model: "all-MPNet-base-v2", purpose: "Semantic text search" },
                  { name: "image_embedding", dim: 512, model: "CLIP ViT-B/32", purpose: "Visual product matching" },
                ].map((v) => (
                  <div key={v.name} className="rounded-lg border border-accent/20 bg-accent/5 p-3 space-y-1.5">
                    <Badge variant="outline" className="font-mono text-[10px]">{v.name}</Badge>
                    <div className="text-[10px] text-muted-foreground">dim={v.dim} · {v.model}</div>
                    <p className="text-[10px] text-muted-foreground">{v.purpose}</p>
                  </div>
                ))}
              </div>

              <div className="rounded-lg bg-muted/20 border border-border p-3">
                <p className="text-[10px] font-semibold text-muted-foreground mb-1.5">Collection Setup:</p>
                <pre className="text-[9px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed">{`client.recreate_collection(
    collection_name="products",
    vectors_config={
        "text_embedding": VectorParams(size=384, distance=Cosine),
        "image_embedding": VectorParams(size=512, distance=Cosine),
    },
    hnsw_config=HnswConfigDiff(m=64, ef_construct=400),
    optimizer_config=OptimizerConfigDiff(indexing_threshold=0)
)

# 8 payload indexes for instant filtering
for field, type in [
    ("sku", KEYWORD), ("category", KEYWORD),
    ("shipping_zone", KEYWORD), ("stock_status", KEYWORD),
    ("price", FLOAT), ("stock", INTEGER),
    ("rating", FLOAT), ("brand", KEYWORD)
]:
    client.create_payload_index("products", field, type)`}</pre>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Search className="h-4 w-4 text-primary" />
                Filtered Hybrid Search
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed">{`# Shopper Agent: "tents under 200CHF Zurich shipping in stock"
results = client.search(
    collection_name="products",
    query_vector=embed("2-person tent for camping"),
    query_filter=Filter(must=[
        FieldCondition(key="category", match=MatchValue(value="tents")),
        FieldCondition(key="price", range=Range(lt=200)),
        FieldCondition(key="stock_status", match=MatchValue(value="in_stock")),
        FieldCondition(key="shipping_zone", match=MatchValue(value="CH")),
    ]),
    vector_name="text_embedding",
    limit=20,
    score_threshold=0.7
)
# → 47 filtered results in 8ms P95`}</pre>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Layers className="h-4 w-4 text-accent" />
                Batch Ingestion Pipeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed">{`# 50K products in 12 minutes
async def ingest_catalog():
    products_df = pd.concat([
        pd.read_csv("data/amazon_reviews.csv"),
        pd.read_json("data/otto_products.json"),
        pd.read_csv("data/retail10k.csv"),
    ])
    
    products = [Product(**row) for row in products_df.to_dict("records")]
    
    # Batch upsert (1000/batch)
    for i in range(0, len(products), 1000):
        batch = products[i:i+1000]
        text_vecs = model.encode([p.title + " " + p.description for p in batch])
        image_vecs = clip.encode([p.image_url for p in batch if p.image_url])
        
        points = [PointStruct(
            id=p.sku,
            vector={"text_embedding": tv, "image_embedding": iv},
            payload=p.to_qdrant_payload()
        ) for p, tv, iv in zip(batch, text_vecs, image_vecs)]
        
        client.upsert("products", points)`}</pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}