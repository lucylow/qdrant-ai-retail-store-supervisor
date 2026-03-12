import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import {
  Database, Server, Search, Filter, Zap, Shield, Package,
  ShoppingCart, Brain, CheckCircle2, ArrowRight, Play, Clock,
  Layers, TrendingUp, Eye, Copy, Activity
} from "lucide-react";
import { cn } from "@/lib/utils";

// ─── Collection Configurations ───────────────────────────────────────────────

const COLLECTIONS = [
  {
    name: "goals",
    purpose: "Blackboard / Task Queue",
    desc: "Shared task board where Shopper writes new goals, Inventory polls for work.",
    icon: ShoppingCart,
    color: "text-primary",
    borderColor: "border-primary/30",
    vectorConfig: { size: 384, distance: "COSINE", model: "all-mpnet-base-v2" },
    optimizers: { indexing_threshold: 0, memmap_threshold: 10000 },
    payloadSchema: {
      goalId: "goal-123",
      userId: "user123",
      status: "open",
      structured: {
        category: "camping",
        budgetMax: 200,
        location: "Zurich",
        deadline: "2026-03-13",
        quantity: 2,
        colorPref: null,
      },
      agentAssignments: ["inventory", "pricing"],
      solutionIds: [],
      createdAt: "2026-03-11T13:48:00Z",
      region: "CH",
    },
    indexes: [
      { field: "status", type: "KEYWORD", reason: "Fast polling for open goals" },
      { field: "userId", type: "KEYWORD", reason: "Per-user goal lookup" },
      { field: "region", type: "KEYWORD", reason: "Regional filtering" },
    ],
    queryPattern: {
      agent: "Inventory Agent",
      label: "Poll for work",
      code: `client.scroll(
    collection_name="goals",
    scroll_filter=Filter(
        must=[FieldCondition(
            key="status",
            match=MatchValue(value="open")
        )]
    ),
    limit=10,
    with_payload=True,
    with_vectors=False  # Don't need vectors for polling
)`,
    },
    perf: { readQps: 1000, writeQps: 100, latency: "<10ms" },
  },
  {
    name: "solutions",
    purpose: "Working Memory",
    desc: "Inventory writes candidate bundles, Shopper reads to present options.",
    icon: Package,
    color: "text-accent",
    borderColor: "border-accent/30",
    vectorConfig: { size: 384, distance: "COSINE", model: "all-mpnet-base-v2" },
    optimizers: { indexing_threshold: 0, memmap_threshold: 10000 },
    payloadSchema: {
      solutionId: "sol-456",
      goalId: "goal-123",
      agentId: "inventory",
      products: [
        { sku: "TENT-XYZ", qty: 1, price: 120 },
        { sku: "MAT-ABC", qty: 2, price: 30 },
      ],
      summary: "2-person tent bundle, 180CHF, Fri delivery",
      totalPrice: 180,
      etaDays: 2,
      confidence: 0.87,
      feasible: true,
      outcome: "pending",
      marginBand: "high",
    },
    indexes: [
      { field: "goalId", type: "KEYWORD", reason: "Link solutions to goals" },
      { field: "outcome", type: "KEYWORD", reason: "Filter by status" },
      { field: "agentId", type: "KEYWORD", reason: "Agent-specific queries" },
    ],
    queryPattern: {
      agent: "Shopper Agent",
      label: "Get solutions for goal",
      code: `client.search(
    collection_name="solutions",
    query_vector=goal_vector,
    query_filter=Filter(
        must=[FieldCondition(
            key="goalId",
            match=MatchValue(value="goal-123")
        )]
    ),
    limit=5
)`,
    },
    perf: { readQps: 500, writeQps: 50, latency: "<15ms" },
  },
  {
    name: "goal_solution_links",
    purpose: "Episodic Memory (MOST IMPORTANT)",
    desc: "Learning memory of what worked/failed. Both agents read this for RAG context.",
    icon: Brain,
    color: "text-status-online",
    borderColor: "border-status-online/30",
    vectorConfig: { size: 384, distance: "COSINE", model: "all-mpnet-base-v2" },
    optimizers: { indexing_threshold: 0, memmap_threshold: 50000 },
    payloadSchema: {
      episodeId: "ep-789",
      goalId: "goal-123",
      solutionId: "sol-456",
      userId: "user123",
      success: true,
      revenue: 180,
      feedbackTags: ["good_value", "fast_delivery"],
      marginBand: "high",
      region: "CH",
      category: "camping",
      timestamp: "2026-03-11T14:00:00Z",
    },
    indexes: [
      { field: "success", type: "KEYWORD", reason: "Filter successful episodes for RAG" },
      { field: "userId", type: "KEYWORD", reason: "Per-user episode retrieval" },
      { field: "category", type: "KEYWORD", reason: "Category-scoped learning" },
      { field: "region", type: "KEYWORD", reason: "Regional episode filtering" },
    ],
    queryPattern: {
      agent: "Both Agents",
      label: "RAG: similar successful episodes",
      code: `client.search(
    collection_name="goal_solution_links",
    query_vector=embed("2-person tent under 200CHF"),
    query_filter=Filter(
        must=[FieldCondition(
            key="success",
            match=MatchValue(value=True)
        )]
    ),
    limit=5
)`,
    },
    perf: { readQps: 2000, writeQps: 10, latency: "<20ms" },
  },
  {
    name: "products",
    purpose: "Domain Knowledge",
    desc: "Semantic product search + constraint filtering for Inventory agent.",
    icon: Database,
    color: "text-status-info",
    borderColor: "border-status-info/30",
    vectorConfig: { size: 384, distance: "COSINE", model: "all-mpnet-base-v2" },
    optimizers: { indexing_threshold: 0, memmap_threshold: 20000 },
    payloadSchema: {
      sku: "TENT-XYZ",
      title: "Alpine 2-Person Tent",
      categoryPath: ["camping", "tents", "2-person"],
      price: 120,
      stockStatus: "in_stock",
      shippingZones: ["CH", "DE", "AT"],
      etaDays: { CH: 2, DE: 3 },
    },
    indexes: [
      { field: "stockStatus", type: "KEYWORD", reason: "Filter in-stock products" },
      { field: "shippingZones", type: "KEYWORD", reason: "Regional availability" },
      { field: "price", type: "FLOAT", reason: "Budget range filtering" },
    ],
    queryPattern: {
      agent: "Inventory Agent",
      label: "Semantic product search with filters",
      code: `client.search(
    collection_name="products",
    query_vector=embed("lightweight 2-person tent"),
    query_filter=Filter(
        must=[
            FieldCondition(key="stockStatus",
                match=MatchValue(value="in_stock")),
            FieldCondition(key="price",
                range=Range(lte=200))
        ]
    ),
    limit=12
)`,
    },
    perf: { readQps: 5000, writeQps: 1000, latency: "<5ms" },
  },
];

// ─── Component ───────────────────────────────────────────────────────────────

export default function QdrantCollections() {
  const [activeCollection, setActiveCollection] = useState("goals");
  const [copied, setCopied] = useState<string | null>(null);

  const copyCode = useCallback((code: string, id: string) => {
    navigator.clipboard.writeText(code).catch(() => {});
    setCopied(id);
    setTimeout(() => setCopied(null), 1500);
  }, []);

  const active = COLLECTIONS.find((c) => c.name === activeCollection)!;

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Database className="h-6 w-6 text-primary" />
          Qdrant Collection Configuration
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Exact vector dimensions, distance metrics, payload indexes, and query patterns for Shopper + Inventory agents
        </p>
      </div>

      {/* Collection selector */}
      <div className="flex flex-wrap gap-2">
        {COLLECTIONS.map((col) => {
          const Icon = col.icon;
          const isActive = activeCollection === col.name;
          return (
            <button
              key={col.name}
              onClick={() => setActiveCollection(col.name)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all",
                isActive
                  ? `${col.borderColor} bg-card shadow-md`
                  : "border-border text-muted-foreground hover:text-foreground hover:border-border"
              )}
            >
              <Icon className={cn("h-4 w-4", isActive ? col.color : "text-muted-foreground")} />
              <span className="font-mono">{col.name}</span>
              {col.name === "goal_solution_links" && (
                <Badge variant="destructive" className="text-[9px] px-1.5 py-0">KEY</Badge>
              )}
            </button>
          );
        })}
      </div>

      {/* Active collection detail */}
      <div className="space-y-4">
        {/* Overview card */}
        <Card className={cn("border-2", active.borderColor)}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base flex items-center gap-2">
                <active.icon className={cn("h-5 w-5", active.color)} />
                <code className="font-mono">{active.name}</code>
                <span className="text-muted-foreground font-normal text-sm">— {active.purpose}</span>
              </CardTitle>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-[10px] font-mono">{active.vectorConfig.size}-dim</Badge>
                <Badge variant="outline" className="text-[10px]">{active.vectorConfig.distance}</Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">{active.desc}</p>

            {/* Vector config + performance */}
            <div className="grid sm:grid-cols-3 gap-3 mb-4">
              <div className="rounded-lg bg-muted/30 border border-border p-3 text-center">
                <p className="text-xs text-muted-foreground">Read QPS</p>
                <p className="text-xl font-bold text-primary">{active.perf.readQps.toLocaleString()}</p>
              </div>
              <div className="rounded-lg bg-muted/30 border border-border p-3 text-center">
                <p className="text-xs text-muted-foreground">Write QPS</p>
                <p className="text-xl font-bold text-accent">{active.perf.writeQps.toLocaleString()}</p>
              </div>
              <div className="rounded-lg bg-muted/30 border border-border p-3 text-center">
                <p className="text-xs text-muted-foreground">Typical Latency</p>
                <p className="text-xl font-bold text-status-online">{active.perf.latency}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="schema" className="space-y-4">
          <TabsList>
            <TabsTrigger value="schema">Payload Schema</TabsTrigger>
            <TabsTrigger value="indexes">Payload Indexes</TabsTrigger>
            <TabsTrigger value="query">Query Pattern</TabsTrigger>
            <TabsTrigger value="setup">Setup Code</TabsTrigger>
          </TabsList>

          {/* Payload Schema */}
          <TabsContent value="schema">
            <Card className="border-border">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Layers className="h-4 w-4" /> Payload Schema
                  </CardTitle>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-xs gap-1"
                    onClick={() => copyCode(JSON.stringify(active.payloadSchema, null, 2), `schema-${active.name}`)}
                  >
                    {copied === `schema-${active.name}` ? <CheckCircle2 className="h-3 w-3 text-status-online" /> : <Copy className="h-3 w-3" />}
                    Copy
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted/50 p-4 rounded-lg text-xs font-mono overflow-x-auto leading-relaxed">
                  {JSON.stringify(active.payloadSchema, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Indexes */}
          <TabsContent value="indexes">
            <Card className="border-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Filter className="h-4 w-4" /> Payload Indexes ({active.indexes.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {active.indexes.map((idx) => (
                  <div key={idx.field} className="rounded-lg border border-border p-3 flex items-start gap-3">
                    <Badge variant="outline" className="text-[10px] font-mono shrink-0 mt-0.5">{idx.type}</Badge>
                    <div>
                      <code className="text-xs font-mono text-primary">{idx.field}</code>
                      <p className="text-[11px] text-muted-foreground mt-0.5">{idx.reason}</p>
                    </div>
                  </div>
                ))}

                <div className="mt-2">
                  <p className="text-xs text-muted-foreground mb-2 font-medium">Index creation code:</p>
                  <pre className="bg-muted/50 p-3 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
{active.indexes.map((idx) =>
  `client.create_payload_index(\n    "${active.name}", "${idx.field}",\n    PayloadSchemaType.${idx.type}\n)`
).join("\n\n")}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Query Pattern */}
          <TabsContent value="query">
            <Card className="border-border">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Search className="h-4 w-4" />
                    {active.queryPattern.agent}: {active.queryPattern.label}
                  </CardTitle>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-xs gap-1"
                    onClick={() => copyCode(active.queryPattern.code, `query-${active.name}`)}
                  >
                    {copied === `query-${active.name}` ? <CheckCircle2 className="h-3 w-3 text-status-online" /> : <Copy className="h-3 w-3" />}
                    Copy
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted/50 p-4 rounded-lg text-xs font-mono overflow-x-auto leading-relaxed">
                  {active.queryPattern.code}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Setup Code */}
          <TabsContent value="setup">
            <Card className="border-border">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <Server className="h-4 w-4" /> Collection Creation
                  </CardTitle>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-xs gap-1"
                    onClick={() => copyCode(
                      `client.create_collection(\n    collection_name="${active.name}",\n    vectors_config=VectorParams(\n        size=${active.vectorConfig.size},\n        distance=Distance.${active.vectorConfig.distance}\n    ),\n    optimizers_config=OptimizersConfigDiff(\n        indexing_threshold=${active.optimizers.indexing_threshold},\n        memmap_threshold=${active.optimizers.memmap_threshold}\n    )\n)`,
                      `setup-${active.name}`
                    )}
                  >
                    {copied === `setup-${active.name}` ? <CheckCircle2 className="h-3 w-3 text-status-online" /> : <Copy className="h-3 w-3" />}
                    Copy
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted/50 p-4 rounded-lg text-xs font-mono overflow-x-auto leading-relaxed">
{`client.create_collection(
    collection_name="${active.name}",
    vectors_config=VectorParams(
        size=${active.vectorConfig.size},
        distance=Distance.${active.vectorConfig.distance}
    ),
    optimizers_config=OptimizersConfigDiff(
        indexing_threshold=${active.optimizers.indexing_threshold},
        memmap_threshold=${active.optimizers.memmap_threshold},
    )
)`}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Performance comparison table */}
      <Card className="border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" />
            Query Performance Comparison
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Collection</TableHead>
                <TableHead>Read QPS</TableHead>
                <TableHead>Write QPS</TableHead>
                <TableHead>Index Fields</TableHead>
                <TableHead>Latency</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {COLLECTIONS.map((col) => (
                <TableRow
                  key={col.name}
                  className={cn("cursor-pointer", activeCollection === col.name && "bg-muted/50")}
                  onClick={() => setActiveCollection(col.name)}
                >
                  <TableCell className="font-mono text-xs font-medium">{col.name}</TableCell>
                  <TableCell className="font-bold text-primary">{col.perf.readQps.toLocaleString()}</TableCell>
                  <TableCell>{col.perf.writeQps.toLocaleString()}</TableCell>
                  <TableCell>
                    <div className="flex gap-1 flex-wrap">
                      {col.indexes.map((idx) => (
                        <Badge key={idx.field} variant="outline" className="text-[9px] font-mono">{idx.field}</Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell className="text-status-online font-bold">{col.perf.latency}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <p className="text-[11px] text-muted-foreground mt-3 italic">
            Supports 10K concurrent users with sub-50ms agent coordination loops. Payload indexes ensure RAG queries execute in one hop.
          </p>
        </CardContent>
      </Card>

      {/* Complete setup script */}
      <Card className="border-border">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" />
              Complete Setup Script
            </CardTitle>
            <Button
              size="sm"
              variant="ghost"
              className="text-xs gap-1"
              onClick={() => copyCode(SETUP_SCRIPT, "full-setup")}
            >
              {copied === "full-setup" ? <CheckCircle2 className="h-3 w-3 text-status-online" /> : <Copy className="h-3 w-3" />}
              Copy All
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <pre className="bg-muted/50 p-4 rounded-lg text-[11px] font-mono overflow-x-auto leading-relaxed">
            {SETUP_SCRIPT}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}

// ─── Full setup script ───────────────────────────────────────────────────────

const SETUP_SCRIPT = `from qdrant_client import QdrantClient, models

client = QdrantClient(":memory:")  # Use cloud URL in production

collections_config = {
    "goals":              {"size": 384, "memmap": 10000},
    "solutions":          {"size": 384, "memmap": 10000},
    "goal_solution_links":{"size": 384, "memmap": 50000},
    "products":           {"size": 384, "memmap": 20000},
}

for name, cfg in collections_config.items():
    client.create_collection(
        collection_name=name,
        vectors_config=models.VectorParams(
            size=cfg["size"],
            distance=models.Distance.COSINE
        ),
        optimizers_config=models.OptimizersConfigDiff(
            indexing_threshold=0,
            memmap_threshold=cfg["memmap"]
        )
    )

# Payload indexes
client.create_payload_index("goals", "status", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("goals", "userId", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("goals", "region", models.PayloadSchemaType.KEYWORD)

client.create_payload_index("solutions", "goalId", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("solutions", "outcome", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("solutions", "agentId", models.PayloadSchemaType.KEYWORD)

client.create_payload_index("goal_solution_links", "success", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("goal_solution_links", "userId", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("goal_solution_links", "category", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("goal_solution_links", "region", models.PayloadSchemaType.KEYWORD)

client.create_payload_index("products", "stockStatus", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("products", "shippingZones", models.PayloadSchemaType.KEYWORD)
client.create_payload_index("products", "price", models.PayloadSchemaType.FLOAT)

print("All collections and indexes created.")`;
