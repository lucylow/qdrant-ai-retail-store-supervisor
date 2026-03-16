import { useState, useCallback } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Wrench, Search, Database, Users, Package, DollarSign, Truck,
  Shield, Lock, ArrowRight, CheckCircle2, XCircle, Activity,
  Play, RotateCcw, Clock, Eye, Layers, Server, Cpu, Bot,
  BookOpen, AlertTriangle, Zap, Globe, FileCode2,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  Types & Data                                                       */
/* ------------------------------------------------------------------ */

interface MCPTool {
  name: string;
  endpoint: string;
  method: "GET" | "POST" | "PATCH";
  agent: "shopper" | "inventory" | "shared";
  category: "read" | "write" | "transactional";
  icon: typeof Search;
  color: string;
  description: string;
  latencyTarget: string;
  requestExample: string;
  responseExample: string;
}

const MCP_TOOLS: MCPTool[] = [
  {
    name: "Catalog Search",
    endpoint: "POST /tools/catalog/search",
    method: "POST",
    agent: "shopper",
    category: "read",
    icon: Search,
    color: "bg-primary/20 text-primary",
    description: "Semantic vector + payload search over product catalog via Qdrant. Returns ranked SKUs with feasibility filters (stock, region, price).",
    latencyTarget: "<200ms",
    requestExample: `{
  "query": "blue t-shirt under 30",
  "filters": {
    "stock_gt": 0,
    "region": "EU",
    "price_lte": 30
  },
  "top_k": 12,
  "mmr": true
}`,
    responseExample: `{
  "results": [
    {
      "sku": "TSHIRT-BLUE-M",
      "product_id": 1001,
      "score": 0.92,
      "payload": {
        "stock": 12,
        "price": 19.99,
        "region": "EU"
      }
    }
  ],
  "retrieval_meta": {
    "vector_model": "all-mpnet-base-v2",
    "embed_ts": "2026-03-11T12:00:00Z"
  }
}`,
  },
  {
    name: "Attribute Schema",
    endpoint: "GET /tools/catalog/schema",
    method: "GET",
    agent: "shopper",
    category: "read",
    icon: FileCode2,
    color: "bg-primary/20 text-primary",
    description: "Introspect available attributes for a category/SKU to build targeted clarification questions instead of vague followups.",
    latencyTarget: "<100ms",
    requestExample: `GET /tools/catalog/schema?category=apparel`,
    responseExample: `{
  "category": "apparel",
  "attributes": [
    {"name":"color","type":"keyword"},
    {"name":"size","type":"keyword"},
    {"name":"material","type":"keyword"},
    {"name":"last_updated","type":"datetime"}
  ],
  "version": "v1.2"
}`,
  },
  {
    name: "User Profile",
    endpoint: "GET /tools/user/{userId}",
    method: "GET",
    agent: "shopper",
    category: "read",
    icon: Users,
    color: "bg-primary/20 text-primary",
    description: "Read persistent user preferences, lifetime value, risk profile from Qdrant user_profiles. Inject into goal extraction prompt.",
    latencyTarget: "<150ms",
    requestExample: `GET /tools/user/user123`,
    responseExample: `{
  "userId": "user123",
  "preferences": {
    "brands": ["MSR", "Big Agnes"],
    "priceSensitivity": "medium",
    "deliveryTolerance": "2-3 days"
  },
  "lifetimeValue": 1250.0,
  "vector_meta": {
    "embed_model": "all-mpnet-base-v2"
  }
}`,
  },
  {
    name: "Warehouse Stock",
    endpoint: "GET /tools/warehouse/stock",
    method: "GET",
    agent: "inventory",
    category: "read",
    icon: Package,
    color: "bg-accent/20 text-accent",
    description: "Authoritative SKU availability & ETA per warehouse. Agents must honor last_synced to avoid stale proposals.",
    latencyTarget: "<200ms",
    requestExample: `GET /tools/warehouse/stock?sku=TSHIRT-BLUE-M&region=EU`,
    responseExample: `{
  "sku": "TSHIRT-BLUE-M",
  "total_stock": 12,
  "warehouse_breakdown": [
    {"wh_id":"WH-ZUR","stock":10,"eta_days":1},
    {"wh_id":"WH-EU-BASE","stock":2,"eta_days":3}
  ],
  "last_synced": "2026-03-11T12:01:00Z"
}`,
  },
  {
    name: "Pricing Engine",
    endpoint: "POST /tools/pricing/quote",
    method: "POST",
    agent: "inventory",
    category: "read",
    icon: DollarSign,
    color: "bg-accent/20 text-accent",
    description: "Compute sell price, discounts, bundle pricing, taxes, regional rounding. Deterministic rules — never LLM-generated.",
    latencyTarget: "<500ms",
    requestExample: `{
  "skus": ["TSHIRT-BLUE-M", "GIFT-WRAP-STD"],
  "region": "EU",
  "coupon": "SPRING10",
  "user_id": "user123"
}`,
    responseExample: `{
  "total": 21.50,
  "breakdown": [
    {"sku":"TSHIRT-BLUE-M","price":19.99},
    {"sku":"GIFT-WRAP-STD","price":2.99}
  ],
  "tax": 1.80,
  "discount": 2.28,
  "final": 21.51
}`,
  },
  {
    name: "Shipping Estimator",
    endpoint: "POST /tools/shipping/estimate",
    method: "POST",
    agent: "inventory",
    category: "read",
    icon: Truck,
    color: "bg-accent/20 text-accent",
    description: "Given dimensions/weight and origin/destination, return ETA & cost per carrier option.",
    latencyTarget: "<300ms",
    requestExample: `{
  "origin": "WH-ZUR",
  "destination": "Zurich",
  "items": [{"sku":"TSHIRT-BLUE-M","qty":1}]
}`,
    responseExample: `{
  "carrier": "DHL",
  "service": "Express",
  "cost": 6.50,
  "eta_days": 2,
  "constraints": {"max_weight": 20}
}`,
  },
  {
    name: "Reserve Stock",
    endpoint: "POST /tools/reservations/reserve",
    method: "POST",
    agent: "inventory",
    category: "transactional",
    icon: Lock,
    color: "bg-chart-4/20 text-chart-4",
    description: "Soft hold on inventory with TTL (10-15 min). Returns reservation_id + expiry. Supports idempotency via Idempotency-Key header.",
    latencyTarget: "<400ms",
    requestExample: `{
  "items": [{"sku":"TSHIRT-BLUE-M","qty":1}],
  "user_id": "user123",
  "idempotency_key": "idem-abc-123"
}`,
    responseExample: `{
  "reservation_id": "res-789",
  "expires_at": "2026-03-11T12:20:00Z",
  "reserved_items": [
    {"sku":"TSHIRT-BLUE-M","qty":1,"wh":"WH-ZUR"}
  ]
}`,
  },
  {
    name: "Confirm Order",
    endpoint: "POST /tools/reservations/confirm",
    method: "POST",
    agent: "inventory",
    category: "transactional",
    icon: CheckCircle2,
    color: "bg-chart-2/20 text-chart-2",
    description: "Convert reservation → order (hard commit, deducts stock). Idempotent — repeated calls with same key are safe.",
    latencyTarget: "<500ms",
    requestExample: `{
  "reservation_id": "res-789",
  "idempotency_key": "idem-abc-123",
  "payment_token": "tok_xyz"
}`,
    responseExample: `{
  "order_id": "ord-456",
  "status": "confirmed",
  "payment_required": false,
  "items": [
    {"sku":"TSHIRT-BLUE-M","qty":1,"price":19.99}
  ]
}`,
  },
  {
    name: "Qdrant Memory Facade",
    endpoint: "POST /tools/memory/{action}",
    method: "POST",
    agent: "shared",
    category: "read",
    icon: Database,
    color: "bg-chart-2/20 text-chart-2",
    description: "Canonical wrapper for all Qdrant reads/writes. Enforces schema, vector model versioning, and returns payload + vector_meta. Agents never call Qdrant directly.",
    latencyTarget: "<200ms",
    requestExample: `{
  "action": "search_episodes",
  "query_text": "camping tent zurich",
  "filters": {"success": true},
  "limit": 3
}`,
    responseExample: `{
  "results": [
    {
      "episode_id": "ep-456",
      "score": 0.91,
      "payload": {
        "goal_summary": "2-person tent Zurich",
        "outcome": "purchased",
        "revenue": 185
      }
    }
  ],
  "vector_meta": {
    "model": "all-mpnet-base-v2",
    "collection": "goal_solution_links"
  }
}`,
  },
];

/* ------------------------------------------------------------------ */
/*  1 · Tool Catalog tab                                               */
/* ------------------------------------------------------------------ */

function ToolCatalogTab() {
  const [expanded, setExpanded] = useState<string | null>(null);

  const groupedByAgent = {
    shopper: MCP_TOOLS.filter((t) => t.agent === "shopper"),
    inventory: MCP_TOOLS.filter((t) => t.agent === "inventory"),
    shared: MCP_TOOLS.filter((t) => t.agent === "shared"),
  };

  const agentMeta = {
    shopper: { label: "Shopper Agent Tools", icon: Bot, color: "text-primary" },
    inventory: { label: "Inventory Agent Tools", icon: Cpu, color: "text-accent" },
    shared: { label: "Shared Tools", icon: Database, color: "text-chart-2" },
  };

  return (
    <div className="space-y-6">
      {(Object.entries(groupedByAgent) as [keyof typeof agentMeta, MCPTool[]][]).map(([agent, tools]) => {
        const meta = agentMeta[agent];
        const Icon = meta.icon;
        return (
          <div key={agent}>
            <div className="flex items-center gap-2 mb-3">
              <Icon className={`h-4 w-4 ${meta.color}`} />
              <h2 className="text-sm font-semibold text-foreground">{meta.label}</h2>
              <Badge variant="outline" className="text-[10px]">{tools.length} tools</Badge>
            </div>
            <div className="space-y-2">
              {tools.map((tool) => {
                const TIcon = tool.icon;
                const isOpen = expanded === tool.name;
                return (
                  <Card key={tool.name} className="border-border bg-card">
                    <CardHeader className="pb-0 cursor-pointer" onClick={() => setExpanded(isOpen ? null : tool.name)}>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-xs flex items-center gap-2">
                          <TIcon className={`h-3.5 w-3.5 ${tool.color.split(" ")[1]}`} />
                          {tool.name}
                          <Badge className={tool.color + " text-[10px]"}>{tool.category}</Badge>
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <code className="text-[10px] font-mono text-muted-foreground">{tool.endpoint}</code>
                          <Badge variant="outline" className="text-[10px]">{tool.latencyTarget}</Badge>
                          <ArrowRight className={`h-3 w-3 text-muted-foreground transition-transform ${isOpen ? "rotate-90" : ""}`} />
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className={`${isOpen ? "pt-3" : "pt-1 pb-3"}`}>
                      <p className="text-[11px] text-muted-foreground mb-2">{tool.description}</p>
                      {isOpen && (
                        <div className="grid md:grid-cols-2 gap-3 mt-3">
                          <div>
                            <p className="text-[10px] text-muted-foreground mb-1 font-medium">Request</p>
                            <pre className="text-[10px] font-mono bg-muted/40 rounded p-2 text-muted-foreground whitespace-pre-wrap">{tool.requestExample}</pre>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground mb-1 font-medium">Response</p>
                            <pre className="text-[10px] font-mono bg-muted/40 rounded p-2 text-muted-foreground whitespace-pre-wrap">{tool.responseExample}</pre>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  2 · Agent Integration tab                                          */
/* ------------------------------------------------------------------ */

function AgentIntegrationTab() {
  const rules = [
    { rule: "Read authoritative facts from MCP before generating any claim about stock/price/ETA", icon: Shield, importance: "critical" },
    { rule: "Only use LLMs for understanding & planning (goal extraction, ranking rationale) — never for facts", icon: AlertTriangle, importance: "critical" },
    { rule: "Include provenance metadata (source, timestamp) when injecting tool responses into prompts", icon: Eye, importance: "high" },
    { rule: "If MCP returns stale data (last_synced > TTL), agent asks user to confirm or triggers live sync", icon: Clock, importance: "high" },
    { rule: "Side-effectful tools (reserve, confirm) require idempotency keys and user authentication", icon: Lock, importance: "critical" },
    { rule: "Agents call Tool Gateway endpoints — never databases or internal services directly", icon: Server, importance: "critical" },
  ];

  const shopperFlow = [
    { step: "Parse user text → structured goal", tool: null },
    { step: "Call user/profile (MCP) for preferences", tool: "User Profile" },
    { step: "Call catalog/schema for attribute introspection", tool: "Attribute Schema" },
    { step: "Build clarifying question if needed", tool: null },
    { step: "Write goal to Qdrant via memory facade", tool: "Qdrant Memory" },
    { step: "Poll solutions for this goal_id", tool: "Qdrant Memory" },
    { step: "Present options with provenance", tool: null },
  ];

  const inventoryFlow = [
    { step: "Poll goals with status='open'", tool: "Qdrant Memory" },
    { step: "Search episodic memory for precedents", tool: "Qdrant Memory" },
    { step: "Catalog search for feasible products", tool: "Catalog Search" },
    { step: "Check warehouse stock per SKU", tool: "Warehouse Stock" },
    { step: "Get pricing quotes for bundles", tool: "Pricing Engine" },
    { step: "Estimate shipping cost & ETA", tool: "Shipping Estimator" },
    { step: "Reserve top candidate (soft hold)", tool: "Reserve Stock" },
    { step: "Write solutions + provisional episode", tool: "Qdrant Memory" },
  ];

  return (
    <div className="space-y-6">
      {/* Policy rules */}
      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Shield className="h-4 w-4 text-destructive" /> Agent Policy Rules
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {rules.map((r) => (
            <div key={r.rule} className="flex items-start gap-3 bg-muted/40 rounded p-2">
              <r.icon className={`h-4 w-4 mt-0.5 shrink-0 ${r.importance === "critical" ? "text-destructive" : "text-chart-4"}`} />
              <div className="text-xs">
                <span className="text-foreground">{r.rule}</span>
                <Badge className={`ml-2 text-[9px] ${r.importance === "critical" ? "bg-destructive/20 text-destructive" : "bg-chart-4/20 text-chart-4"}`}>{r.importance}</Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Agent flows */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Bot className="h-4 w-4 text-primary" /> Shopper Agent Flow
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5">
              {shopperFlow.map((s, i) => (
                <div key={i} className="flex items-center gap-2 text-[11px]">
                  <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center text-[9px] font-bold text-primary shrink-0">{i + 1}</div>
                  <span className="text-muted-foreground flex-1">{s.step}</span>
                  {s.tool && <Badge variant="outline" className="text-[9px] shrink-0">{s.tool}</Badge>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Cpu className="h-4 w-4 text-accent" /> Inventory Agent Flow
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5">
              {inventoryFlow.map((s, i) => (
                <div key={i} className="flex items-center gap-2 text-[11px]">
                  <div className="w-5 h-5 rounded-full bg-accent/20 flex items-center justify-center text-[9px] font-bold text-accent shrink-0">{i + 1}</div>
                  <span className="text-muted-foreground flex-1">{s.step}</span>
                  {s.tool && <Badge variant="outline" className="text-[9px] shrink-0">{s.tool}</Badge>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  3 · Transactions tab                                               */
/* ------------------------------------------------------------------ */

function TransactionsTab() {
  const [simStep, setSimStep] = useState(-1);
  const [running, setRunning] = useState(false);

  const steps = [
    { label: "Inventory agent selects top bundle", icon: Cpu, color: "text-accent" },
    { label: "POST /tools/reservations/reserve (idempotency_key: idem-abc)", icon: Lock, color: "text-chart-4" },
    { label: "Stock soft-locked: TSHIRT-BLUE-M × 1 (TTL: 15min)", icon: Package, color: "text-chart-4" },
    { label: "Shopper presents option to user", icon: Bot, color: "text-primary" },
    { label: "User confirms → POST /tools/reservations/confirm", icon: CheckCircle2, color: "text-chart-2" },
    { label: "Stock deducted, order created: ord-456", icon: Zap, color: "text-chart-2" },
    { label: "Episode written to goal_solution_links", icon: Database, color: "text-accent" },
  ];

  const runSim = useCallback(async () => {
    setSimStep(-1);
    setRunning(true);
    for (let i = 0; i < steps.length; i++) {
      setSimStep(i);
      await new Promise((r) => setTimeout(r, 700));
    }
    setRunning(false);
  }, []);

  const patterns = [
    { title: "Idempotency", desc: "Accept Idempotency-Key header; repeated calls with same key return cached result. Prevents double-charge.", icon: Shield },
    { title: "Reservation TTL", desc: "Reservations expire after 10-15 min. Background job auto-releases expired holds to prevent indefinite stock locks.", icon: Clock },
    { title: "Optimistic Locking", desc: "Use compare-and-swap or DB transactions when confirming. Concurrent workers mark goals status=in_progress before processing.", icon: Lock },
    { title: "Compensation", desc: "If confirm fails (payment timeout), run compensation to restore stock and notify user. Log failure episode.", icon: AlertTriangle },
  ];

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        {patterns.map((p) => (
          <Card key={p.title} className="border-border bg-card">
            <CardContent className="pt-4 space-y-2">
              <div className="flex items-center gap-2">
                <p.icon className="h-4 w-4 text-chart-4" />
                <p className="text-sm font-medium text-foreground">{p.title}</p>
              </div>
              <p className="text-xs text-muted-foreground">{p.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Play className="h-4 w-4 text-primary" /> Reserve → Confirm Flow
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Button size="sm" onClick={runSim} disabled={running} className="gap-1 text-xs">
              <Play className="h-3 w-3" /> Simulate
            </Button>
            <Button size="sm" variant="outline" onClick={() => { setSimStep(-1); setRunning(false); }} className="gap-1 text-xs">
              <RotateCcw className="h-3 w-3" /> Reset
            </Button>
          </div>
          <div className="space-y-1.5">
            {steps.map((s, i) => {
              const active = i === simStep;
              const done = simStep > i;
              return (
                <div key={i} className={`flex items-center gap-3 px-3 py-2 rounded-lg border transition-all ${active ? "border-primary bg-primary/10 scale-[1.01]" : done ? "border-chart-2/20 bg-chart-2/5 opacity-60" : "border-border bg-card"}`}>
                  <s.icon className={`h-4 w-4 shrink-0 ${active ? "text-primary" : done ? "text-chart-2" : s.color}`} />
                  <span className="text-xs flex-1 text-muted-foreground">{s.label}</span>
                  {done && <CheckCircle2 className="h-3 w-3 text-chart-2" />}
                  {active && <span className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  4 · Security & Observability tab                                   */
/* ------------------------------------------------------------------ */

function SecurityTab() {
  const security = [
    { area: "Service Tokens + RBAC", desc: "Read-only for Shopper, write/reserve for Inventory. Fine-grained permissions per tool.", icon: Lock },
    { area: "User Auth", desc: "reservation/confirm endpoints require user session token. Prevents unauthorized stock holds.", icon: Users },
    { area: "PII Handling", desc: "user_profiles encrypted at rest. Audit logs use hashed IDs. 'Forget me' API for GDPR Art 17.", icon: Shield },
    { area: "Rate Limiting", desc: "Per-user and per-agent rate limits enforced at gateway. Prevents abuse and DDoS.", icon: AlertTriangle },
  ];

  const metrics = [
    { metric: "Tool Call Latency (p95)", value: "180ms", target: "<200ms", status: "ok" },
    { metric: "Reservation Success Rate", value: "99.4%", target: ">99%", status: "ok" },
    { metric: "Stale Data Rate", value: "2.1%", target: "<5%", status: "ok" },
    { metric: "Idempotency Hit Rate", value: "3.8%", target: "—", status: "info" },
    { metric: "Confirm Error Rate", value: "0.3%", target: "<0.5%", status: "ok" },
    { metric: "Episodic Reuse Rate", value: "62%", target: ">50%", status: "ok" },
  ];

  const observability = [
    "Structured call logs: request, response, source_ids, embed_model_version",
    "Replayable traces: full prompt + MCP results for debugging hallucinations",
    "SLA alerts: reservation/confirm error rate > 0.5% or warehouse latency > 500ms",
    "Training signals: tool call outcomes feed episodic memory for model improvement",
  ];

  const gatewayCode = `# MCP Gateway (FastAPI — minimal)
from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()

class CatalogSearchReq(BaseModel):
    query: str
    filters: dict = {}
    top_k: int = 8

@app.post("/tools/catalog/search")
async def catalog_search(
    req: CatalogSearchReq,
    x_service_token: str = Header(...)
):
    # 1. Validate RBAC token
    # 2. Compute embedding (or accept precomputed)
    # 3. Call Qdrant: search + payload filters
    # 4. Return typed response with retrieval_meta
    return {
        "results": [...],
        "retrieval_meta": {
            "vector_model": "all-mpnet-base-v2",
            "ts": "2026-03-11T12:00:00Z"
        }
    }

class ReserveReq(BaseModel):
    items: list
    user_id: str
    idempotency_key: str | None = None

@app.post("/tools/reservations/reserve")
async def reserve(
    req: ReserveReq,
    idempotency_key: str = Header(None)
):
    # 1. Check idempotency store (Redis)
    # 2. Validate stock availability
    # 3. Create reservation row with TTL
    # 4. Return reservation_id + expires_at
    return {
        "reservation_id": "res-789",
        "expires_at": "2026-03-11T12:20:00Z",
        "reserved_items": req.items
    }`;

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-3">
        {security.map((s) => (
          <Card key={s.area} className="border-border bg-card">
            <CardContent className="pt-4 space-y-1.5">
              <div className="flex items-center gap-2">
                <s.icon className="h-4 w-4 text-chart-4" />
                <p className="text-sm font-medium text-foreground">{s.area}</p>
              </div>
              <p className="text-xs text-muted-foreground">{s.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary" /> MCP Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-3 gap-3">
            {metrics.map((m) => (
              <div key={m.metric} className="bg-muted/40 rounded p-2 space-y-1">
                <p className="text-[10px] text-muted-foreground">{m.metric}</p>
                <p className="text-lg font-bold text-foreground">{m.value}</p>
                <div className="flex items-center gap-1">
                  <Badge className={`text-[9px] ${m.status === "ok" ? "bg-chart-2/20 text-chart-2" : "bg-muted text-muted-foreground"}`}>
                    {m.status === "ok" ? "✓" : "ℹ"} {m.target}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Eye className="h-4 w-4 text-accent" /> Observability
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {observability.map((o, i) => (
              <li key={i} className="flex gap-2 text-xs text-muted-foreground">
                <CheckCircle2 className="h-3.5 w-3.5 text-chart-2 mt-0.5 shrink-0" />
                {o}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Server className="h-4 w-4 text-primary" /> Gateway Implementation
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[360px]">
            <pre className="text-[10px] font-mono p-4 text-muted-foreground leading-relaxed whitespace-pre-wrap">{gatewayCode}</pre>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Root page                                                          */
/* ------------------------------------------------------------------ */

export default function MCPToolsPage() {
  return (
    <div className="p-4 md:p-6 space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Wrench className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-bold text-foreground">MCP Tools</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Model-Controller-Proxy tooling layer — deterministic APIs that agents call for authoritative facts, side-effects, and guardrails.
        </p>
      </div>

      <Tabs defaultValue="catalog" className="space-y-4">
        <TabsList className="bg-muted/50 h-auto flex-wrap gap-1">
          <TabsTrigger value="catalog" className="text-xs gap-1"><Wrench className="h-3 w-3" /> Tool Catalog</TabsTrigger>
          <TabsTrigger value="integration" className="text-xs gap-1"><Layers className="h-3 w-3" /> Agent Integration</TabsTrigger>
          <TabsTrigger value="transactions" className="text-xs gap-1"><Lock className="h-3 w-3" /> Transactions</TabsTrigger>
          <TabsTrigger value="security" className="text-xs gap-1"><Shield className="h-3 w-3" /> Security & Ops</TabsTrigger>
        </TabsList>

        <TabsContent value="catalog"><ToolCatalogTab /></TabsContent>
        <TabsContent value="integration"><AgentIntegrationTab /></TabsContent>
        <TabsContent value="transactions"><TransactionsTab /></TabsContent>
        <TabsContent value="security"><SecurityTab /></TabsContent>
      </Tabs>
    </div>
  );
}
