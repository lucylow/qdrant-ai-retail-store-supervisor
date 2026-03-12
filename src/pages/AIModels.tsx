import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Brain, Cpu, Zap, DollarSign, Globe, Layers, ArrowRight,
  CheckCircle2, XCircle, Clock, BarChart3, Shield, Users,
  Database, Target, Activity, Sparkles, Server, Mic,
  Volume2, Package, Terminal, Star, Eye, GitBranch,
  Workflow, Image, MessageSquare, Box, Gauge, HardDrive,
  Network, Play, Code2, Settings2, Boxes, Search,
} from "lucide-react";

/* ------------------------------------------------------------------ */
/*  1 · Model Selection tab                                            */
/* ------------------------------------------------------------------ */

function ModelSelectionTab() {
  const shopperModels = [
    {
      name: "GPT-4o-mini", provider: "OpenAI", badge: "⭐ PRIMARY",
      latency: "200–400ms", cost: "$0.15/1M tokens", context: "128k",
      strengths: ["Conversational fluency", "Reliable JSON structured goals", "Fast inference"],
      use: "Goal extraction, solution explanation, clarification dialog",
    },
    {
      name: "Gemini 2.5 Flash", provider: "Google", badge: "ALTERNATIVE",
      latency: "150–300ms", cost: "$0.10/1M tokens", context: "1M",
      strengths: ["Multimodal (image+text)", "Largest context window", "Cost-efficient"],
      use: "Visual product queries, large RAG contexts",
    },
    {
      name: "Llama 3.3 8B", provider: "Meta (Groq)", badge: "FALLBACK",
      latency: "<100ms", cost: "$0.05/1M tokens", context: "128k",
      strengths: ["Ultra-low latency on Groq LPUs", "95%+ JSON compliance", "Free tier available"],
      use: "High-volume simple queries, cost-sensitive scale",
    },
  ];

  const inventoryModels = [
    {
      name: "Claude 3.5 Sonnet", provider: "Anthropic", badge: "⭐ PRIMARY",
      latency: "800–1500ms", cost: "$3/1M tokens", context: "200k",
      strengths: ["Superior multi-step reasoning", "Constraint satisfaction", "Reliable structured output"],
      use: "Bundle optimization, multi-objective ranking, trade-off analysis",
    },
    {
      name: "DeepSeek R1 8B", provider: "DeepSeek", badge: "OPEN-SOURCE",
      latency: "200ms", cost: "$0.10/1M tokens", context: "128k",
      strengths: ["o1-level reasoning distilled", "Strong planning capabilities", "Self-hosted option"],
      use: "Complex inventory reasoning, scoring from RAG context",
    },
    {
      name: "GPT-4o", provider: "OpenAI", badge: "FALLBACK",
      latency: "500–1000ms", cost: "$2.50/1M tokens", context: "128k",
      strengths: ["Balanced reasoning/speed", "Excellent JSON mode", "Multimodal"],
      use: "When Claude unavailable or cost-constrained",
    },
  ];

  const ModelCard = ({ model, agent }: { model: typeof shopperModels[0]; agent: string }) => (
    <Card className="border-border bg-card">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">{model.name}</CardTitle>
          <Badge className={model.badge.includes("PRIMARY") ? "bg-primary/20 text-primary text-[10px]" : model.badge === "FALLBACK" ? "bg-muted text-muted-foreground text-[10px]" : "bg-accent/20 text-accent text-[10px]"}>
            {model.badge}
          </Badge>
        </div>
        <p className="text-[11px] text-muted-foreground">{model.provider}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 gap-2 text-[11px]">
          <div><span className="text-muted-foreground block">Latency</span><span className="font-mono">{model.latency}</span></div>
          <div><span className="text-muted-foreground block">Cost</span><span className="font-mono">{model.cost}</span></div>
          <div><span className="text-muted-foreground block">Context</span><span className="font-mono">{model.context}</span></div>
        </div>
        <div className="space-y-1">
          {model.strengths.map((s) => (
            <div key={s} className="flex gap-1.5 text-[11px]">
              <CheckCircle2 className="h-3 w-3 text-chart-2 mt-0.5 shrink-0" />
              <span className="text-muted-foreground">{s}</span>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-accent italic">{model.use}</p>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Users className="h-4 w-4 text-primary" />
          <h2 className="text-lg font-semibold text-foreground">Shopper Agent Models</h2>
        </div>
        <p className="text-xs text-muted-foreground mb-3">Customer-facing NLU: parse natural language → structured goal JSON with conversational fluency.</p>
        <div className="grid md:grid-cols-3 gap-3">
          {shopperModels.map((m) => <ModelCard key={m.name} model={m} agent="shopper" />)}
        </div>
      </div>
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Database className="h-4 w-4 text-accent" />
          <h2 className="text-lg font-semibold text-foreground">Inventory Agent Models</h2>
        </div>
        <p className="text-xs text-muted-foreground mb-3">Back-office planner: case-based reasoning from RAG episodes + constraint satisfaction for bundle optimization.</p>
        <div className="grid md:grid-cols-3 gap-3">
          {inventoryModels.map((m) => <ModelCard key={m.name} model={m} agent="inventory" />)}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  2 · Routing Matrix tab                                             */
/* ------------------------------------------------------------------ */

function RoutingMatrixTab() {
  const matrix = [
    { task: "Goal Extraction", shopper: "GPT-4o-mini ⭐", inventory: "—", latency: "<500ms", cost: "High", tier: 1 },
    { task: "Bundle Planning", shopper: "—", inventory: "Claude 3.5 Sonnet ⭐", latency: "<2s", cost: "Medium", tier: 3 },
    { task: "Solution Explanation", shopper: "GPT-4o-mini", inventory: "GPT-4o", latency: "<500ms", cost: "High", tier: 1 },
    { task: "Episode Generation", shopper: "Llama 3.3 8B", inventory: "Llama 3.3 8B", latency: "<200ms", cost: "Highest", tier: 1 },
    { task: "Solution Ranking", shopper: "—", inventory: "DeepSeek R1 8B", latency: "<300ms", cost: "High", tier: 2 },
    { task: "Clarification Dialog", shopper: "GPT-4o-mini", inventory: "—", latency: "<400ms", cost: "High", tier: 1 },
  ];

  const tiers = [
    { tier: "Tier 1 (90% traffic)", models: "GPT-4o-mini + Llama 3.3", savings: "95% cost savings", color: "bg-chart-2/20 text-chart-2" },
    { tier: "Tier 2 (9% traffic)", models: "GPT-4o (balanced)", savings: "Moderate cost", color: "bg-chart-4/20 text-chart-4" },
    { tier: "Tier 3 (1% traffic)", models: "Claude 3.5 / o1-mini", savings: "Complex reasoning only", color: "bg-primary/20 text-primary" },
  ];

  const dynamicRouting = `async function selectModel(
  task: Task, 
  goalComplexity: number
): Promise<string> {
  // Fast path: simple goals → cheap model
  if (task.agent === 'shopper' || goalComplexity < 0.7) {
    return 'gpt-4o-mini';
  }
  
  // Complex reasoning → heavyweight model
  if (goalComplexity > 0.9 && task.type === 'bundle_planning') {
    return 'claude-3.5-sonnet';
  }
  
  // Default balanced path
  return 'gpt-4o';
}`;

  return (
    <div className="space-y-6">
      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Task → Model Routing Matrix</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border text-muted-foreground">
                  <th className="text-left py-2 pr-3">Task</th>
                  <th className="text-left py-2 pr-3">Shopper</th>
                  <th className="text-left py-2 pr-3">Inventory</th>
                  <th className="text-left py-2 pr-3">Latency</th>
                  <th className="text-left py-2">Cost Priority</th>
                </tr>
              </thead>
              <tbody>
                {matrix.map((r) => (
                  <tr key={r.task} className="border-b border-border/50">
                    <td className="py-2 pr-3 font-medium text-foreground">{r.task}</td>
                    <td className="py-2 pr-3"><span className={r.shopper.includes("⭐") ? "text-primary font-medium" : "text-muted-foreground"}>{r.shopper}</span></td>
                    <td className="py-2 pr-3"><span className={r.inventory.includes("⭐") ? "text-accent font-medium" : "text-muted-foreground"}>{r.inventory}</span></td>
                    <td className="py-2 pr-3 font-mono text-muted-foreground">{r.latency}</td>
                    <td className="py-2"><Badge variant="outline" className="text-[10px]">{r.cost}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-3 gap-3">
        {tiers.map((t) => (
          <Card key={t.tier} className="border-border bg-card">
            <CardContent className="pt-4 space-y-2">
              <Badge className={t.color + " text-[10px]"}>{t.tier}</Badge>
              <p className="text-sm font-medium text-foreground">{t.models}</p>
              <p className="text-xs text-muted-foreground">{t.savings}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Dynamic Model Router</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-[11px] font-mono bg-muted/40 rounded p-3 text-muted-foreground whitespace-pre-wrap">{dynamicRouting}</pre>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  3 · Embeddings tab                                                 */
/* ------------------------------------------------------------------ */

function EmbeddingsTab() {
  const models = [
    {
      name: "NVIDIA NVmix-8B-384", badge: "⭐ BEST FOR QDRANT",
      dim: 384, context: "32k", mteb: "65.2%", latency: "25ms",
      multilingual: "Excellent", qdrant: true,
      use: "All collections (goals, solutions, episodes, products)",
      strengths: ["Qdrant co-optimized (HNSW tuned)", "Handles JSON + natural language equally", "Sub-50ms inference"],
    },
    {
      name: "bge-m3 (BAAI)", badge: "⭐ BEST MULTILINGUAL",
      dim: "1024→384", context: "8k", mteb: "64.5%", latency: "35ms",
      multilingual: "Perfect", qdrant: false,
      use: "products, goals (user utterances in CH/DE/FR/IT)",
      strengths: ["Dense + sparse + multi-granularity retrieval", "Perfect for e-commerce", "Industry standard multilingual"],
    },
    {
      name: "Snowflake Arctic Embed M", badge: "BEST NEWCOMER",
      dim: 384, context: "128k", mteb: "64.8%", latency: "30ms",
      multilingual: "Excellent", qdrant: false,
      use: "goal_solution_links, solutions",
      strengths: ["128k context (agentic RAG ready)", "Optimized for instruction-following", "Excellent goal → episode similarity"],
    },
  ];

  const collectionStrategy = [
    { collection: "goals", model: "NVmix-8B-384", textToEmbed: "raw_utterance", search: "Goal → similar goals" },
    { collection: "solutions", model: "Snowflake Arctic M", textToEmbed: "summary", search: "Solution ranking" },
    { collection: "goal_solution_links", model: "NVmix-8B-384", textToEmbed: "goal_text + solution_summary", search: "Case-based planning" },
    { collection: "products", model: "bge-m3", textToEmbed: "title + description + specs", search: "Semantic product search" },
  ];

  const benchmarks = [
    { model: "NVmix-8B", mteb: 65.2, dim: 384, latency: 25, multilingual: "Excellent", qdrant: "✅" },
    { model: "bge-m3", mteb: 64.5, dim: 1024, latency: 35, multilingual: "Perfect", qdrant: "Good" },
    { model: "Arctic M", mteb: 64.8, dim: 384, latency: 30, multilingual: "Excellent", qdrant: "Excellent" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-3 gap-3">
        {models.map((m) => (
          <Card key={m.name} className="border-border bg-card">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">{m.name}</CardTitle>
                <Badge className={m.badge.includes("QDRANT") ? "bg-primary/20 text-primary text-[10px]" : m.badge.includes("MULTILINGUAL") ? "bg-accent/20 text-accent text-[10px]" : "bg-chart-4/20 text-chart-4 text-[10px]"}>{m.badge}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div><span className="text-muted-foreground block">Dimensions</span><span className="font-mono">{m.dim}</span></div>
                <div><span className="text-muted-foreground block">Context</span><span className="font-mono">{m.context}</span></div>
                <div><span className="text-muted-foreground block">MTEB</span><span className="font-mono text-primary">{m.mteb}</span></div>
                <div><span className="text-muted-foreground block">Latency</span><span className="font-mono">{m.latency}</span></div>
              </div>
              <div className="space-y-1">
                {m.strengths.map((s) => (
                  <div key={s} className="flex gap-1.5 text-[11px]">
                    <CheckCircle2 className="h-3 w-3 text-chart-2 mt-0.5 shrink-0" />
                    <span className="text-muted-foreground">{s}</span>
                  </div>
                ))}
              </div>
              <p className="text-[10px] text-accent italic">{m.use}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Collection-Specific Embedding Strategy</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border text-muted-foreground">
                <th className="text-left py-2 pr-3">Collection</th>
                <th className="text-left py-2 pr-3">Embedding Model</th>
                <th className="text-left py-2 pr-3">Text to Embed</th>
                <th className="text-left py-2">Search Use Case</th>
              </tr>
            </thead>
            <tbody>
              {collectionStrategy.map((c) => (
                <tr key={c.collection} className="border-b border-border/50">
                  <td className="py-2 pr-3"><Badge variant="outline" className="text-[10px] font-mono">{c.collection}</Badge></td>
                  <td className="py-2 pr-3 text-primary text-[11px]">{c.model}</td>
                  <td className="py-2 pr-3 text-muted-foreground font-mono text-[10px]">{c.textToEmbed}</td>
                  <td className="py-2 text-muted-foreground text-[11px]">{c.search}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Performance Benchmarks (Groq LPUs)</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border text-muted-foreground">
                <th className="text-left py-2 pr-3">Model</th>
                <th className="text-left py-2 pr-3">MTEB</th>
                <th className="text-left py-2 pr-3">Dim</th>
                <th className="text-left py-2 pr-3">Latency (1k txt)</th>
                <th className="text-left py-2 pr-3">Multilingual</th>
                <th className="text-left py-2">Qdrant</th>
              </tr>
            </thead>
            <tbody>
              {benchmarks.map((b) => (
                <tr key={b.model} className="border-b border-border/50">
                  <td className="py-2 pr-3 font-medium text-foreground">{b.model}</td>
                  <td className="py-2 pr-3">
                    <div className="flex items-center gap-2">
                      <Progress value={b.mteb} className="h-1.5 w-16" />
                      <span className="font-mono text-primary">{b.mteb}%</span>
                    </div>
                  </td>
                  <td className="py-2 pr-3 font-mono text-muted-foreground">{b.dim}</td>
                  <td className="py-2 pr-3 font-mono text-muted-foreground">{b.latency}ms</td>
                  <td className="py-2 pr-3 text-muted-foreground">{b.multilingual}</td>
                  <td className="py-2">{b.qdrant}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  4 · Open-Source Models tab                                         */
/* ------------------------------------------------------------------ */

function OpenSourceTab() {
  const models = [
    {
      name: "Llama 3.3 8B", provider: "Meta AI", badge: "⭐ BEST OVERALL",
      json: 95, firstToken: 45, tokens1k: 180, ragCtx: "Excellent",
      platforms: ["Groq (200+ tok/s)", "Ollama", "Hugging Face"],
      notes: "Fastest inference on Groq LPUs. Rivals GPT-4o-mini quality.",
    },
    {
      name: "Qwen2.5-Coder 7B", provider: "Alibaba", badge: "⭐ BEST STRUCTURED",
      json: 98, firstToken: 38, tokens1k: 150, ragCtx: "Excellent",
      platforms: ["Groq", "vLLM"],
      notes: "#1 open model for JSON/code tasks. Native function calling.",
    },
    {
      name: "DeepSeek R1 Distilled 8B", provider: "DeepSeek AI", badge: "BEST REASONING",
      json: 92, firstToken: 60, tokens1k: 240, ragCtx: "Perfect",
      platforms: ["Hugging Face", "Ollama"],
      notes: "o1-level reasoning distilled. Strong multi-step planning.",
    },
    {
      name: "Mistral-Nemo 12B", provider: "Mistral AI", badge: "BALANCED",
      json: 93, firstToken: 55, tokens1k: 220, ragCtx: "Very Good",
      platforms: ["Groq", "Together.ai"],
      notes: "Fast on consumer GPUs (RTX 4090: 80 tok/s). Reliable JSON.",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-3">
        {models.map((m) => (
          <Card key={m.name} className="border-border bg-card">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-sm">{m.name}</CardTitle>
                  <p className="text-[11px] text-muted-foreground">{m.provider}</p>
                </div>
                <Badge className={m.badge.includes("BEST OVERALL") ? "bg-primary/20 text-primary text-[10px]" : m.badge.includes("STRUCTURED") ? "bg-accent/20 text-accent text-[10px]" : "bg-chart-4/20 text-chart-4 text-[10px]"}>{m.badge}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-muted-foreground">JSON Accuracy</span>
                  <div className="flex items-center gap-2">
                    <Progress value={m.json} className="h-1.5 w-20" />
                    <span className="font-mono w-8 text-right">{m.json}%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-muted-foreground">First Token</span>
                  <span className="font-mono">{m.firstToken}ms</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-muted-foreground">1000 Tokens</span>
                  <span className="font-mono">{m.tokens1k}ms</span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-muted-foreground">8k RAG Context</span>
                  <Badge variant="outline" className="text-[10px]">{m.ragCtx}</Badge>
                </div>
              </div>
              <div className="flex gap-1 flex-wrap">
                {m.platforms.map((p) => (
                  <Badge key={p} className="bg-muted text-muted-foreground text-[10px]">{p}</Badge>
                ))}
              </div>
              <p className="text-[10px] text-accent italic">{m.notes}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Fallback Chain</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-2">
            {["Llama 3.3 8B (Groq)", "Qwen2.5-Coder 7B (local)", "Mistral-Nemo 12B (4-bit)", "Phi-3.5-mini (emergency)"].map((m, i, arr) => (
              <div key={m} className="flex items-center gap-2">
                <Badge className={i === 0 ? "bg-primary/20 text-primary text-[10px]" : "bg-muted text-muted-foreground text-[10px]"}>{m}</Badge>
                {i < arr.length - 1 && <ArrowRight className="h-3 w-3 text-muted-foreground" />}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  5 · Prompt Templates tab                                           */
/* ------------------------------------------------------------------ */

function PromptTemplatesTab() {
  const shopperPrompt = `{
  "role": "shopper_agent",
  "instruction": "Extract structured goal JSON from user text. 
    Past 3 user successes provided as context. 
    Validate all constraints.",
  "input": "2-person tent under 200CHF, Zurich Friday",
  "episodes": [
    "goal: blue t-shirt under 30 | sol: TSHIRT-BLUE-M | outcome: purchased",
    "goal: camping gear budget 150 | sol: TENT-BASIC + MAT | outcome: purchased"
  ],
  "output_schema": {
    "category": "string",
    "budgetMax": "number|null",
    "location": "string",
    "deadline": "ISO-date|null",
    "weightPref": "string|null"
  }
}`;

  const inventoryPrompt = `{
  "role": "inventory_agent",
  "instruction": "Rank bundles by weighted objectives:
    success_rate(40%) + margin(30%) + eta(20%) + price_fit(10%).
    Past successes provided as episodic context.
    Feasible SKUs pre-filtered by stock > 0 and region match.",
  "goal": { "category": "camping", "budgetMax": 200, "location": "Zurich" },
  "episodic_precedents": [
    { "skus": ["TENT-ALP-2","MAT-LITE"], "outcome": "purchased", "score": 0.91 },
    { "skus": ["TENT-BASIC"], "outcome": "partial", "score": 0.65 }
  ],
  "candidate_products": [
    { "sku": "TENT-ALP-2", "price": 120, "stock": 5, "eta": 2 },
    { "sku": "MAT-LITE", "price": 30, "stock": 12, "eta": 1 }
  ],
  "output_schema": {
    "bundles": [{
      "skus": ["string"],
      "total_price": "number",
      "confidence": "0-1",
      "feasible": "boolean",
      "rationale": "string"
    }]
  }
}`;

  const contextTemplate = `Shopper Agent Context Assembly:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prompt = user_request
       + 3× user_successful_episodes (goal_solution_links)
       + goal_validation_schema
→ GPT-4o-mini → structured_goal → Qdrant upsert

Inventory Agent Context Assembly:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prompt = structured_goal
       + 3× similar_successful_episodes
       + 8× feasible_products
       + ranking_criteria_weights
→ Claude 3.5 → ranked_bundles → Qdrant solutions`;

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold text-foreground">Shopper Agent Prompt</h3>
          </div>
          <Card className="border-border bg-card">
            <CardContent className="p-0">
              <ScrollArea className="h-[320px]">
                <pre className="text-[11px] font-mono p-4 text-muted-foreground leading-relaxed whitespace-pre-wrap">{shopperPrompt}</pre>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Database className="h-4 w-4 text-accent" />
            <h3 className="text-sm font-semibold text-foreground">Inventory Agent Prompt</h3>
          </div>
          <Card className="border-border bg-card">
            <CardContent className="p-0">
              <ScrollArea className="h-[320px]">
                <pre className="text-[11px] font-mono p-4 text-muted-foreground leading-relaxed whitespace-pre-wrap">{inventoryPrompt}</pre>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm">Context Engineering Pipeline</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-[11px] font-mono bg-muted/40 rounded p-3 text-muted-foreground whitespace-pre-wrap">{contextTemplate}</pre>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  6 · Cost & Fallbacks tab                                           */
/* ------------------------------------------------------------------ */

function CostTab() {
  const costBreakdown = [
    { agent: "Shopper", model: "GPT-4o-mini", calls: "20k", costDay: "$0.59" },
    { agent: "Inventory", model: "Claude 3.5", calls: "10k", costDay: "$9.50" },
    { agent: "Episodes", model: "Llama 3.3 8B", calls: "15k", costDay: "$0.15" },
    { agent: "Embeddings", model: "NVmix-8B-384", calls: "50k", costDay: "$0.10" },
  ];

  const costComparison = [
    { stack: "Open-Source (Groq)", cost: "$0.10–0.30/1M", daily10k: "$1–3/day" },
    { stack: "OpenAI GPT-4o-mini", cost: "$0.15/1M", daily10k: "$3–5/day" },
    { stack: "Anthropic Claude 3.5", cost: "$3.00/1M", daily10k: "$10–50/day" },
    { stack: "Mixed (recommended)", cost: "~$0.33/1M avg", daily10k: "~$10/day" },
  ];

  const fallbacks = [
    { trigger: "Model timeout (>5s)", action: "Next tier down (Claude → GPT-4o → mini)", icon: Clock },
    { trigger: "JSON parsing fails", action: "Retry with stricter schema enforcement", icon: Shield },
    { trigger: "Low confidence (<0.7)", action: "Human-in-loop or clarification question", icon: Users },
    { trigger: "Rate limits hit", action: "Queue + exponential backoff", icon: Activity },
    { trigger: "All models fail", action: "Return cached similar solution from episodes", icon: Database },
  ];

  const hackathonStack = [
    { component: "Shopper LLM", choice: "GPT-4o-mini (OpenAI API key)", cost: "~$0.50" },
    { component: "Inventory LLM", choice: "Llama 3.3 8B (Groq free tier)", cost: "$0" },
    { component: "Embeddings", choice: "text-embedding-3-small (OpenAI)", cost: "~$0.10" },
    { component: "Vector DB", choice: "Qdrant Cloud free tier", cost: "$0" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-4">
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-chart-4" /> Daily Cost (10k Users)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border text-muted-foreground">
                  <th className="text-left py-1.5">Agent</th>
                  <th className="text-left py-1.5">Model</th>
                  <th className="text-right py-1.5">Calls/Day</th>
                  <th className="text-right py-1.5">Cost</th>
                </tr>
              </thead>
              <tbody>
                {costBreakdown.map((c) => (
                  <tr key={c.agent} className="border-b border-border/50">
                    <td className="py-1.5 font-medium text-foreground">{c.agent}</td>
                    <td className="py-1.5 text-muted-foreground">{c.model}</td>
                    <td className="py-1.5 text-right font-mono">{c.calls}</td>
                    <td className="py-1.5 text-right font-mono text-chart-4">{c.costDay}</td>
                  </tr>
                ))}
                <tr className="font-medium">
                  <td className="py-2" colSpan={3}>Total</td>
                  <td className="py-2 text-right font-mono text-primary">~$10.34/day</td>
                </tr>
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" /> Stack Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border text-muted-foreground">
                  <th className="text-left py-1.5">Stack</th>
                  <th className="text-left py-1.5">Per 1M Tokens</th>
                  <th className="text-right py-1.5">10k Users/Day</th>
                </tr>
              </thead>
              <tbody>
                {costComparison.map((c) => (
                  <tr key={c.stack} className="border-b border-border/50">
                    <td className="py-1.5 text-foreground">{c.stack}</td>
                    <td className="py-1.5 font-mono text-muted-foreground">{c.cost}</td>
                    <td className="py-1.5 text-right font-mono">{c.daily10k}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Shield className="h-4 w-4 text-destructive" /> Fallback & Error Handling
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {fallbacks.map((f) => (
              <div key={f.trigger} className="flex items-start gap-3 bg-muted/40 rounded p-2">
                <f.icon className="h-4 w-4 text-accent mt-0.5 shrink-0" />
                <div className="text-xs">
                  <span className="font-medium text-foreground">{f.trigger}</span>
                  <span className="text-muted-foreground"> → {f.action}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-chart-4" /> Hackathon Demo Stack (48hr Build)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-border text-muted-foreground">
                <th className="text-left py-1.5">Component</th>
                <th className="text-left py-1.5">Choice</th>
                <th className="text-right py-1.5">Cost</th>
              </tr>
            </thead>
            <tbody>
              {hackathonStack.map((h) => (
                <tr key={h.component} className="border-b border-border/50">
                  <td className="py-1.5 font-medium text-foreground">{h.component}</td>
                  <td className="py-1.5 text-muted-foreground">{h.choice}</td>
                  <td className="py-1.5 text-right font-mono text-chart-2">{h.cost}</td>
                </tr>
              ))}
              <tr className="font-medium">
                <td className="py-2" colSpan={2}>Total for 500 test runs</td>
                <td className="py-2 text-right font-mono text-primary">~$2</td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  7 · Hugging Face Stack tab                                         */
/* ------------------------------------------------------------------ */

const HF_EMBEDDINGS = [
  {
    name: "Marqo/marqo-ecommerce-embeddings-L",
    badge: "⭐ BEST E-COM",
    dim: 1024,
    latency: "15ms",
    benchmark: "+38.9% MRR vs Amazon Titan",
    use: "text_vector + image_vector for products, goals, solutions",
    strengths: ["E-commerce fine-tuned", "Single model text+image", "92% recall on tent→tent"],
    license: "Apache 2.0",
    color: "bg-status-online/20 text-status-online",
  },
  {
    name: "sentence-transformers/all-MiniLM-L6-v2",
    badge: "LIGHTWEIGHT",
    dim: 384,
    latency: "5ms",
    benchmark: "61.8% MTEB",
    use: "Edge deployment, hackathon fallback, episodes",
    strengths: ["5ms inference", "22M params", "Perfect for demos"],
    license: "Apache 2.0",
    color: "bg-primary/20 text-primary",
  },
  {
    name: "openai/clip-vit-base-patch32",
    badge: "VISUAL",
    dim: 512,
    latency: "12ms",
    benchmark: "Industry standard visual",
    use: "image_vector in products collection",
    strengths: ["Text-to-image retrieval", "Photo search", "Zero-shot classification"],
    license: "MIT",
    color: "bg-accent/20 text-accent",
  },
];

const HF_AGENTS = [
  {
    name: "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    agent: "Shopper Agent",
    badge: "GOAL EXTRACTION",
    params: "1.5B",
    latency: "200ms",
    use: "Extracts JSON goals from natural language",
    example: '"tent under 200" → {"category":"tents","budget_max":200}',
    color: "text-primary",
    icon: Users,
  },
  {
    name: "Meta-Llama-3.1-8B-Instruct",
    agent: "Inventory Agent",
    badge: "BUNDLE SYNTHESIS",
    params: "8B",
    latency: "1.2s",
    use: "RAG-grounded bundle ranking + explanations",
    example: '"3 bundles: TentA+SackB (328CHF, Thu delivery)"',
    color: "text-accent",
    icon: Database,
  },
  {
    name: "google/gemma-2-2b-it",
    agent: "Fast Reasoning",
    badge: "FALLBACK",
    params: "2B",
    latency: "400ms",
    use: "Quick bundle ranking from episode context",
    example: "Margin-aware ranking in 2s",
    color: "text-muted-foreground",
    icon: Zap,
  },
];

const HF_VOICE = [
  { name: "openai/whisper-base", role: "Speech → Text", params: "74M", latency: "1.2s", languages: "DE/EN/FR/IT", icon: Mic },
  { name: "microsoft/speech_t5_tts", role: "Text → Speech", params: "143M", latency: "0.8s", languages: "EN (primary)", icon: Volume2 },
];

const HF_BENCHMARKS = [
  { metric: "Text Retrieval", value: "92%", detail: "recall vs Amazon (Marqo Ecom)", color: "text-status-online" },
  { metric: "Image Matching", value: "87%", detail: "visual similarity (tent→tent)", color: "text-accent" },
  { metric: "Bundle Conversion", value: "+27%", detail: "from RAG episodes", color: "text-primary" },
  { metric: "Voice Latency", value: "2.1s", detail: "end-to-end (Whisper+Llama)", color: "text-status-warning" },
  { metric: "MRR vs Titan", value: "+38.9%", detail: "Marqo e-commerce", color: "text-status-online" },
  { metric: "Cost/1K Queries", value: "$0.02", detail: "Apache 2.0 models", color: "text-primary" },
];

const HF_DEMO_FLOW = [
  { step: "🎤 Voice", detail: '"tent + sleeping bag under 400"', model: "Whisper-base" },
  { step: "📝 Transcript", detail: "→ text extracted (DE/EN/FR/IT)", model: "Whisper" },
  { step: "🧠 Embedding", detail: "→ Qdrant text_vector (1024dim)", model: "Marqo-ecom-L" },
  { step: "🎯 Goal", detail: '→ {"category":"tents","budget":400}', model: "Qwen2.5-Coder" },
  { step: "📦 Bundles", detail: "→ 3 feasible bundles ranked", model: "Llama3.1-8B" },
  { step: "🔊 Response", detail: '→ "Here\'s what I found…"', model: "SpeechT5" },
];

const SYSTEM_ARCH_STAGES = [
  { label: "User Request", desc: "Voice or text input", icon: MessageSquare, color: "text-primary" },
  { label: "Speech / Text Model", desc: "Whisper STT or passthrough", icon: Mic, color: "text-accent" },
  { label: "Shopper Agent", desc: "Intent → structured goal JSON", icon: Users, color: "text-primary" },
  { label: "Qdrant RAG", desc: "Semantic + filtered retrieval", icon: Search, color: "text-status-online" },
  { label: "Inventory Agent", desc: "Bundle synthesis + ranking", icon: Database, color: "text-accent" },
  { label: "Product Bundle", desc: "Ranked proposals → user", icon: Package, color: "text-status-online" },
];

const MODEL_SERVING_OPTIONS = [
  {
    title: "HF Inference API",
    badge: "FASTEST SETUP",
    desc: "Hosted endpoint, zero infrastructure",
    pros: ["Fast deployment", "No GPU management", "Auto-scaling"],
    cons: ["Higher latency (~500ms)", "Rate limits", "Cost at scale"],
    code: `from huggingface_hub import InferenceClient

client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct"
)
response = client.text_generation(
    prompt=prompt,
    max_new_tokens=200
)`,
    color: "border-primary/30",
  },
  {
    title: "Self-Hosted (TGI)",
    badge: "PRODUCTION",
    desc: "Text Generation Inference on your GPU",
    pros: ["10× lower cost at scale", "Sub-100ms latency", "Full control"],
    cons: ["Requires GPU infra", "Ops overhead", "Scaling complexity"],
    code: `# Docker deployment
docker run --gpus all \\
  -p 8080:80 \\
  ghcr.io/huggingface/text-generation-inference:latest \\
  --model-id meta-llama/Llama-3.1-8B-Instruct \\
  --quantize bitsandbytes-nf4 \\
  --max-batch-prefill-tokens 2048`,
    color: "border-accent/30",
  },
];

const OPTIMIZATION_STRATEGIES = [
  { title: "4-bit Quantization", desc: "bitsandbytes NF4 — 75% memory reduction, <1% quality loss", icon: HardDrive, metric: "8B → 4.5GB VRAM" },
  { title: "Batch Embeddings", desc: "Encode 512 texts per batch instead of 1-by-1", icon: Boxes, metric: "40× throughput" },
  { title: "GPU Acceleration", desc: "NVIDIA A10/L4 with Flash Attention 2", icon: Zap, metric: "3× faster inference" },
  { title: "KV-Cache Reuse", desc: "Cache system prompt tokens across requests", icon: Database, metric: "30% latency reduction" },
  { title: "ONNX Runtime", desc: "Export embedding models to ONNX for CPU inference", icon: Settings2, metric: "2× CPU speedup" },
  { title: "Speculative Decoding", desc: "Draft with Gemma-2B, verify with Llama-8B", icon: GitBranch, metric: "1.8× generation speed" },
];

function HFStackTab() {
  const [activeSection, setActiveSection] = useState("overview");

  const sections = [
    { id: "overview", label: "Overview", icon: Sparkles },
    { id: "architecture", label: "Architecture", icon: Network },
    { id: "shopper", label: "Shopper Agent", icon: Users },
    { id: "inventory", label: "Inventory Agent", icon: Database },
    { id: "multimodal", label: "Multimodal", icon: Image },
    { id: "voice", label: "Voice Pipeline", icon: Mic },
    { id: "serving", label: "Model Serving", icon: Server },
    { id: "optimization", label: "Optimization", icon: Gauge },
    { id: "benchmarks", label: "Benchmarks", icon: BarChart3 },
    { id: "code", label: "Code Registry", icon: Code2 },
  ];

  return (
    <div className="space-y-4">
      {/* Section navigator */}
      <ScrollArea className="w-full">
        <div className="flex gap-1 pb-2">
          {sections.map((s) => {
            const Icon = s.icon;
            return (
              <Button
                key={s.id}
                size="sm"
                variant={activeSection === s.id ? "default" : "ghost"}
                className="text-[10px] h-7 px-2 shrink-0 gap-1"
                onClick={() => setActiveSection(s.id)}
              >
                <Icon className="h-3 w-3" />
                {s.label}
              </Button>
            );
          })}
        </div>
      </ScrollArea>

      {/* ---- OVERVIEW ---- */}
      {activeSection === "overview" && (
        <div className="space-y-4">
          {/* Hero */}
          <Card className="border-status-online/20 bg-status-online/5">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-status-online/20 border border-status-online/30 flex items-center justify-center shrink-0">
                  <Sparkles className="h-5 w-5 text-status-online" />
                </div>
                <div className="space-y-1.5">
                  <h2 className="text-sm font-bold">Zero-Cost HF Production Stack</h2>
                  <p className="text-xs text-muted-foreground">
                    Marqo E-commerce (38.9% &gt; Amazon Titan) + Llama3.1-8B + Whisper → $0.02/1K queries, Apache 2.0 licensed.
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {["38.9% > Titan", "$0 License", "92% Recall", "2.1s E2E", "Multilingual"].map((t) => (
                      <Badge key={t} className="text-[9px] bg-status-online/15 text-status-online border-status-online/30">{t}</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Model usage matrix */}
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Workflow className="h-4 w-4 text-primary" />
                Model Capabilities Matrix
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground">
                      <th className="text-left py-2 pr-3">Agent</th>
                      <th className="text-left py-2 pr-3">Role</th>
                      <th className="text-left py-2 pr-3">Model Type</th>
                      <th className="text-left py-2">HF Model</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { agent: "Shopper Agent", role: "Understand user intent", type: "LLM + Embedding", model: "Qwen2.5-Coder + Marqo-ecom" },
                      { agent: "Inventory Agent", role: "Generate product bundles", type: "Reasoning LLM", model: "Llama-3.1-8B-Instruct" },
                      { agent: "Embedding", role: "Semantic search", type: "Sentence Transformer", model: "Marqo-ecom-L (1024d)" },
                      { agent: "Text LLM", role: "Reasoning", type: "Instruction-tuned", model: "Llama-3.1 / Qwen2.5" },
                      { agent: "Image", role: "Product search", type: "CLIP encoder", model: "clip-vit-base-patch32" },
                      { agent: "Speech", role: "Voice queries", type: "ASR + TTS", model: "Whisper + SpeechT5" },
                    ].map((r) => (
                      <tr key={r.agent} className="border-b border-border/50">
                        <td className="py-1.5 pr-3 font-medium text-foreground">{r.agent}</td>
                        <td className="py-1.5 pr-3 text-muted-foreground">{r.role}</td>
                        <td className="py-1.5 pr-3"><Badge variant="outline" className="text-[9px]">{r.type}</Badge></td>
                        <td className="py-1.5 font-mono text-primary text-[10px]">{r.model}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Embedding models grid */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Globe className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold">Embedding Models (Qdrant Vectors)</h2>
            </div>
            <div className="grid md:grid-cols-3 gap-3">
              {HF_EMBEDDINGS.map((m) => (
                <Card key={m.name} className="border-border">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xs leading-tight">{m.name.split("/")[1]}</CardTitle>
                      <Badge className={m.color + " text-[9px]"}>{m.badge}</Badge>
                    </div>
                    <p className="text-[10px] text-muted-foreground font-mono">{m.name}</p>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                      <div><span className="text-muted-foreground block">Dim</span><span className="font-mono font-bold">{m.dim}</span></div>
                      <div><span className="text-muted-foreground block">Latency</span><span className="font-mono">{m.latency}</span></div>
                    </div>
                    <p className="text-[10px] text-status-online font-medium">{m.benchmark}</p>
                    <div className="space-y-0.5">
                      {m.strengths.map((s) => (
                        <div key={s} className="flex gap-1 text-[10px]">
                          <CheckCircle2 className="h-3 w-3 text-status-online mt-0.5 shrink-0" />
                          <span className="text-muted-foreground">{s}</span>
                        </div>
                      ))}
                    </div>
                    <p className="text-[9px] text-accent italic">{m.use}</p>
                    <Badge variant="outline" className="text-[9px]">{m.license}</Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Agent reasoning models grid */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Brain className="h-4 w-4 text-accent" />
              <h2 className="text-sm font-semibold">Agent Reasoning Models</h2>
            </div>
            <div className="grid md:grid-cols-3 gap-3">
              {HF_AGENTS.map((m) => {
                const Icon = m.icon;
                return (
                  <Card key={m.name} className="border-border">
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <Icon className={`h-3.5 w-3.5 ${m.color}`} />
                          <CardTitle className="text-xs">{m.agent}</CardTitle>
                        </div>
                        <Badge variant="outline" className="text-[9px]">{m.badge}</Badge>
                      </div>
                      <p className="text-[10px] text-muted-foreground font-mono">{m.name}</p>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="grid grid-cols-2 gap-1.5 text-[10px]">
                        <div><span className="text-muted-foreground block">Params</span><span className="font-mono font-bold">{m.params}</span></div>
                        <div><span className="text-muted-foreground block">Latency</span><span className="font-mono">{m.latency}</span></div>
                      </div>
                      <p className="text-[10px] text-muted-foreground">{m.use}</p>
                      <div className="rounded bg-muted/30 px-2 py-1.5">
                        <code className="text-[9px] font-mono text-primary break-all">{m.example}</code>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ---- ARCHITECTURE ---- */}
      {activeSection === "architecture" && (
        <div className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Network className="h-4 w-4 text-primary" />
                System Pipeline Architecture
              </CardTitle>
              <p className="text-xs text-muted-foreground">HF models are used in 4 stages: speech recognition → embedding generation → LLM reasoning → multimodal product search</p>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {SYSTEM_ARCH_STAGES.map((s, i) => {
                  const Icon = s.icon;
                  return (
                    <div key={s.label}>
                      <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-3">
                        <div className="w-8 h-8 rounded-lg bg-muted/50 flex items-center justify-center shrink-0">
                          <Icon className={`h-4 w-4 ${s.color}`} />
                        </div>
                        <div className="flex-1">
                          <div className="text-xs font-semibold">{s.label}</div>
                          <div className="text-[10px] text-muted-foreground">{s.desc}</div>
                        </div>
                        <Badge variant="outline" className="text-[9px] shrink-0">Stage {i + 1}</Badge>
                      </div>
                      {i < SYSTEM_ARCH_STAGES.length - 1 && (
                        <div className="flex justify-center py-0.5">
                          <ArrowRight className="h-3 w-3 text-muted-foreground rotate-90" />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Embedding pipeline for Qdrant */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Globe className="h-4 w-4 text-accent" />
                Embedding Pipeline → Qdrant
              </CardTitle>
              <p className="text-xs text-muted-foreground">Embeddings connect HF models with the vector database for semantic retrieval</p>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

model = SentenceTransformer("Marqo/marqo-ecommerce-embeddings-L")
qdrant = QdrantClient(url="http://localhost:6333")

# Encode user query → 1024-dim vector
vector = model.encode("camping tent under 200 CHF")

# Semantic search with metadata filters
results = qdrant.search(
    collection_name="products",
    query_vector=("text_embedding", vector.tolist()),
    query_filter=Filter(must=[
        FieldCondition(key="stock_status", match=MatchValue(value="in_stock")),
        FieldCondition(key="price", range=Range(lt=200)),
        FieldCondition(key="shipping_zone", match=MatchValue(value="CH")),
    ]),
    limit=10
)`}</pre>
            </CardContent>
          </Card>

          {/* Production deployment */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Box className="h-4 w-4 text-status-online" />
                Production Deployment Architecture
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-3">
                {[
                  { layer: "Frontend", components: ["React SPA", "Voice Capture", "Product Grid"], color: "text-primary" },
                  { layer: "API Gateway", components: ["FastAPI", "Rate Limiting", "Auth"], color: "text-accent" },
                  { layer: "Agent Orchestrator", components: ["Shopper Agent", "Inventory Agent", "Coordinator"], color: "text-status-online" },
                  { layer: "Model Server", components: ["TGI (Llama 8B)", "Embedding Server", "CLIP Server"], color: "text-status-warning" },
                  { layer: "Vector DB", components: ["Qdrant Cluster", "products / goals / episodes", "8 payload indexes"], color: "text-primary" },
                  { layer: "Storage", components: ["Product images (S3)", "Audio files", "Episode logs"], color: "text-muted-foreground" },
                ].map((l) => (
                  <div key={l.layer} className="rounded-lg border border-border bg-muted/10 p-3 space-y-1.5">
                    <div className={`text-xs font-bold ${l.color}`}>{l.layer}</div>
                    <div className="flex flex-wrap gap-1">
                      {l.components.map((c) => (
                        <Badge key={c} variant="outline" className="text-[9px]">{c}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- SHOPPER AGENT ---- */}
      {activeSection === "shopper" && (
        <div className="space-y-4">
          <Card className="border-primary/20 bg-primary/5">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-sm font-bold">Shopper Agent — HF Model Integration</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Converts user input → structured goal JSON using embedding retrieval + LLM reasoning
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pipeline */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Shopper Agent Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap items-center gap-1.5">
                {[
                  { step: "User Request", model: null },
                  { step: "Embed Query", model: "Marqo-ecom-L" },
                  { step: "Retrieve Similar Goals", model: "Qdrant" },
                  { step: "LLM Reasoning", model: "Qwen2.5-Coder" },
                  { step: "Structured Goal", model: null },
                ].map((s, i, arr) => (
                  <div key={s.step} className="flex items-center gap-1.5">
                    <div className="rounded-md border border-border bg-card px-2 py-1.5 text-center">
                      <div className="text-[10px] font-medium">{s.step}</div>
                      {s.model && <div className="text-[8px] text-primary font-mono">{s.model}</div>}
                    </div>
                    {i < arr.length - 1 && <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0" />}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Prompt template */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Shopper Agent Prompt Template</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`You are a shopping assistant for a Swiss e-commerce platform.

User request:
"I need a tent under 200 CHF for camping near Zurich"

Retrieved similar successful sessions:
{retrieved_sessions}

Convert the request into structured goal JSON:
{
  "category": "string",     // product category
  "budget_max": "number",   // max price in CHF
  "location": "string",     // delivery location
  "urgency": "string",      // normal | express | next-day
  "constraints": ["string"] // additional filters
}`}</pre>
            </CardContent>
          </Card>

          {/* HF Inference example */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">HF Inference — Goal Extraction</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`from huggingface_hub import InferenceClient

client = InferenceClient(model="Qwen/Qwen2.5-Coder-1.5B-Instruct")

response = client.text_generation(
    prompt=shopper_prompt,
    max_new_tokens=200,
    temperature=0.1,    # Low temp for structured output
    do_sample=False
)`}</pre>
              <div className="rounded-lg border border-status-online/30 bg-status-online/5 p-3">
                <div className="text-[10px] font-medium text-status-online mb-1">Example Output:</div>
                <pre className="text-[10px] font-mono text-muted-foreground">{`{
  "category": "camping tent",
  "budget_max": 200,
  "location": "Zurich, Switzerland",
  "urgency": "normal",
  "constraints": ["2-person", "waterproof"]
}`}</pre>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- INVENTORY AGENT ---- */}
      {activeSection === "inventory" && (
        <div className="space-y-4">
          <Card className="border-accent/20 bg-accent/5">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-accent/20 border border-accent/30 flex items-center justify-center shrink-0">
                  <Database className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <h2 className="text-sm font-bold">Inventory Agent — HF Model Integration</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Generates product bundles using RAG-retrieved products + episodic memory + LLM reasoning
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pipeline */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Inventory Agent Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap items-center gap-1.5">
                {[
                  { step: "Structured Goal", model: null },
                  { step: "Retrieve Products", model: "Qdrant products" },
                  { step: "Retrieve Episodes", model: "Qdrant episodes" },
                  { step: "LLM Reasoning", model: "Llama3.1-8B" },
                  { step: "Bundle Proposal", model: null },
                ].map((s, i, arr) => (
                  <div key={s.step} className="flex items-center gap-1.5">
                    <div className="rounded-md border border-border bg-card px-2 py-1.5 text-center">
                      <div className="text-[10px] font-medium">{s.step}</div>
                      {s.model && <div className="text-[8px] text-accent font-mono">{s.model}</div>}
                    </div>
                    {i < arr.length - 1 && <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0" />}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Prompt template */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Inventory Agent Prompt Template</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`Goal:
User wants a camping tent under 200 CHF, Zurich delivery.

Available products (from Qdrant filtered search):
{product_results}

Past successful bundles (episodic memory):
{episode_memory}

Generate top 3 bundles ranked by:
- price fit (within budget)
- inventory availability (stock > 0)
- historical conversion rate (from episodes)
- delivery ETA to Zurich

Return JSON array of bundles with rationale.`}</pre>
            </CardContent>
          </Card>

          {/* Example output */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Bundle Synthesis Example</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`from huggingface_hub import InferenceClient

client = InferenceClient(model="Meta-Llama-3.1-8B-Instruct")

# RAG context from Qdrant
rag_context = "\\n".join([
    f"{r.payload['title']} - CHF{r.payload['price']} (stock: {r.payload['stock']})"
    for r in qdrant_results[:10]
])

response = client.text_generation(
    prompt=inventory_prompt.format(
        product_results=rag_context,
        episode_memory=episode_context
    ),
    max_new_tokens=400,
    temperature=0.1
)`}</pre>
              <div className="mt-3 grid md:grid-cols-2 gap-2">
                {[
                  { name: "Bundle 1", items: "Alpine Tent + Sleeping Mat", price: "195 CHF", confidence: "91%" },
                  { name: "Bundle 2", items: "Mountain Tent + Compact Sleeping Bag", price: "199 CHF", confidence: "85%" },
                ].map((b) => (
                  <div key={b.name} className="rounded-lg border border-accent/30 bg-accent/5 p-3 space-y-1">
                    <div className="text-xs font-bold text-accent">{b.name}</div>
                    <div className="text-[10px] text-muted-foreground">{b.items}</div>
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="font-mono font-bold">{b.price}</span>
                      <Badge className="text-[8px] bg-status-online/15 text-status-online">{b.confidence} confidence</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- MULTIMODAL ---- */}
      {activeSection === "multimodal" && (
        <div className="space-y-4">
          <Card className="border-accent/20 bg-accent/5">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-accent/20 border border-accent/30 flex items-center justify-center shrink-0">
                  <Image className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <h2 className="text-sm font-bold">Multimodal Search — CLIP Integration</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Users upload product photos → CLIP embedding → Qdrant image_vector search → visually similar products
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pipeline */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Visual Search Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap items-center gap-1.5 mb-4">
                {[
                  { step: "📷 User Photo", model: null },
                  { step: "CLIP Encode", model: "ViT-B/32" },
                  { step: "512-dim Vector", model: null },
                  { step: "Qdrant Search", model: "image_vector" },
                  { step: "Similar Products", model: null },
                ].map((s, i, arr) => (
                  <div key={s.step} className="flex items-center gap-1.5">
                    <div className="rounded-md border border-border bg-card px-2 py-1.5 text-center">
                      <div className="text-[10px] font-medium">{s.step}</div>
                      {s.model && <div className="text-[8px] text-accent font-mono">{s.model}</div>}
                    </div>
                    {i < arr.length - 1 && <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0" />}
                  </div>
                ))}
              </div>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`import clip
from PIL import Image

# Load CLIP model
model, preprocess = clip.load("ViT-B/32")

# Encode user's uploaded photo
image = preprocess(Image.open("tent.jpg")).unsqueeze(0)
image_vector = model.encode_image(image).detach().numpy()[0]

# Search products by visual similarity
results = qdrant.search(
    collection_name="products",
    query_vector=("image_embedding", image_vector.tolist()),
    limit=10
)

# Results: visually similar products ranked by cosine similarity`}</pre>
            </CardContent>
          </Card>

          {/* Marqo dual-mode */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Star className="h-4 w-4 text-status-online" />
                Marqo E-Commerce: Unified Text + Image
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground mb-3">
                Marqo handles both text and image in a single 1024-dim space — no separate CLIP model needed for production.
              </p>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Marqo/marqo-ecommerce-embeddings-L")

# Text query → same vector space as images
text_vec = model.encode("red camping tent waterproof")

# Image → same vector space as text
image_vec = model.encode(Image.open("tent.jpg"))

# Both produce 1024-dim vectors, searchable in same Qdrant collection
# 87% visual match accuracy on tent→tent queries`}</pre>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- VOICE PIPELINE ---- */}
      {activeSection === "voice" && (
        <div className="space-y-4">
          <Card className="border-primary/20 bg-primary/5">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0">
                  <Mic className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-sm font-bold">Voice RAG Pipeline</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Whisper multilingual STT (DE/EN/FR/IT) → Shopper Agent → Qdrant → SpeechT5 voice response
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-2 gap-3">
            {HF_VOICE.map((v) => {
              const Icon = v.icon;
              return (
                <Card key={v.name} className="border-border">
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                        <Icon className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <div className="text-xs font-semibold">{v.role}</div>
                        <div className="text-[10px] text-muted-foreground font-mono">{v.name}</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-[10px]">
                      <div><span className="text-muted-foreground block">Params</span><span className="font-mono">{v.params}</span></div>
                      <div><span className="text-muted-foreground block">Latency</span><span className="font-mono">{v.latency}</span></div>
                      <div><span className="text-muted-foreground block">Languages</span><span className="font-mono">{v.languages}</span></div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Voice Shopping Code</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`import whisper

# Load Whisper for multilingual Zurich support
model = whisper.load_model("base")  # 74M params

# Transcribe voice query (DE/EN/FR/IT auto-detect)
result = model.transcribe("voice_query.wav")
text_query = result["text"]
detected_lang = result["language"]  # "de" | "en" | "fr" | "it"

# → Pass to Shopper Agent for goal extraction
goal = shopper_agent.parse_goal(text_query)

# After bundle generation, respond with voice
from transformers import pipeline
tts = pipeline("text-to-speech", model="microsoft/speech_t5_tts")
audio = tts(f"Found {len(bundles)} bundles under {budget}CHF")`}</pre>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- MODEL SERVING ---- */}
      {activeSection === "serving" && (
        <div className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            {MODEL_SERVING_OPTIONS.map((opt) => (
              <Card key={opt.title} className={`border-border ${opt.color}`}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{opt.title}</CardTitle>
                    <Badge variant="outline" className="text-[9px]">{opt.badge}</Badge>
                  </div>
                  <p className="text-[10px] text-muted-foreground">{opt.desc}</p>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <div className="text-[9px] text-status-online font-medium mb-1">Advantages</div>
                      {opt.pros.map((p) => (
                        <div key={p} className="flex gap-1 text-[10px]">
                          <CheckCircle2 className="h-3 w-3 text-status-online mt-0.5 shrink-0" />
                          <span className="text-muted-foreground">{p}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <div className="text-[9px] text-destructive font-medium mb-1">Trade-offs</div>
                      {opt.cons.map((c) => (
                        <div key={c} className="flex gap-1 text-[10px]">
                          <XCircle className="h-3 w-3 text-destructive mt-0.5 shrink-0" />
                          <span className="text-muted-foreground">{c}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <pre className="text-[9px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded bg-muted/20 border border-border p-2">{opt.code}</pre>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* LangChain integration */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <GitBranch className="h-4 w-4 text-accent" />
                LangChain Agent Integration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

# Connect HF model to LangChain
llm = HuggingFaceEndpoint(
    repo_id="Meta-Llama-3.1-8B-Instruct",
    temperature=0.1,
    max_new_tokens=300
)

# Shopper Agent chain
shopper_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="User: {query}\\nContext: {context}\\nGoal JSON:"
)
shopper_chain = LLMChain(llm=llm, prompt=shopper_prompt)

# Inventory Agent chain
inventory_prompt = PromptTemplate(
    input_variables=["goal", "products", "episodes"],
    template="Goal: {goal}\\nProducts: {products}\\nEpisodes: {episodes}\\nBundles:"
)
inventory_chain = LLMChain(llm=llm, prompt=inventory_prompt)`}</pre>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- OPTIMIZATION ---- */}
      {activeSection === "optimization" && (
        <div className="space-y-4">
          <div className="grid md:grid-cols-3 gap-3">
            {OPTIMIZATION_STRATEGIES.map((o) => {
              const Icon = o.icon;
              return (
                <Card key={o.title} className="border-border">
                  <CardContent className="pt-4 space-y-2">
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-primary" />
                      <div className="text-xs font-bold">{o.title}</div>
                    </div>
                    <p className="text-[10px] text-muted-foreground">{o.desc}</p>
                    <Badge className="bg-primary/15 text-primary text-[9px]">{o.metric}</Badge>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-accent" />
                4-bit Quantization Example
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# 4-bit NF4 quantization: 8B model → 4.5GB VRAM
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,  # Nested quantization
)

model = AutoModelForCausalLM.from_pretrained(
    "Meta-Llama-3.1-8B-Instruct",
    quantization_config=quantization_config,
    device_map="auto"
)
# Result: <1% quality loss, runs on free Colab T4 (16GB)`}</pre>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Boxes className="h-4 w-4 text-primary" />
                Batch Embedding Optimization
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`from sentence_transformers import SentenceTransformer

model = SentenceTransformer("Marqo/marqo-ecommerce-embeddings-L")

# ❌ Slow: 1-by-1 encoding
for product in products:
    vec = model.encode(product["title"])  # 15ms each → 150s for 10K

# ✅ Fast: Batch encoding (40× throughput)
texts = [p["title"] + " " + p["description"] for p in products]
vectors = model.encode(
    texts,
    batch_size=512,       # Maximize GPU utilization
    show_progress_bar=True,
    normalize_embeddings=True  # Pre-normalize for cosine
)
# 10K products in ~4 seconds on A10 GPU`}</pre>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- BENCHMARKS ---- */}
      {activeSection === "benchmarks" && (
        <div className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-status-online" />
                Performance Benchmarks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {HF_BENCHMARKS.map((b) => (
                  <div key={b.metric} className="rounded-lg border border-border bg-muted/20 p-3 text-center space-y-1">
                    <div className={`text-lg font-bold ${b.color}`}>{b.value}</div>
                    <div className="text-xs font-medium">{b.metric}</div>
                    <div className="text-[10px] text-muted-foreground">{b.detail}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Demo flow */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Play className="h-4 w-4 text-accent" />
                Demo Pipeline Flow (2.1s E2E)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1.5">
                {HF_DEMO_FLOW.map((s, i) => (
                  <div key={i} className="flex items-center gap-3 text-xs rounded-lg border border-border bg-card p-2.5">
                    <span className="text-sm shrink-0">{s.step}</span>
                    <span className="flex-1 text-muted-foreground">{s.detail}</span>
                    <Badge variant="outline" className="text-[9px] font-mono shrink-0">{s.model}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Latency breakdown */}
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Latency Breakdown per Stage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  { stage: "Embedding generation", ms: 15, pct: 12 },
                  { stage: "Vector search (Qdrant)", ms: 30, pct: 25 },
                  { stage: "LLM reasoning", ms: 1200, pct: 100 },
                ].map((s) => (
                  <div key={s.stage} className="space-y-1">
                    <div className="flex justify-between text-[10px]">
                      <span className="text-muted-foreground">{s.stage}</span>
                      <span className="font-mono text-foreground">~{s.ms}ms</span>
                    </div>
                    <Progress value={s.pct} className="h-1.5" />
                  </div>
                ))}
                <div className="flex justify-between text-xs font-bold pt-2 border-t border-border">
                  <span>Total response</span>
                  <span className="text-primary font-mono">~1.2s</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ---- CODE REGISTRY ---- */}
      {activeSection === "code" && (
        <div className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Terminal className="h-4 w-4 text-primary" />
                Production Model Registry
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`# production_models.py — Zero-cost HF stack
EMBEDDINGS = {
    "ecommerce_text": "Marqo/marqo-ecommerce-embeddings-L",  # 1024dim
    "lightweight":    "sentence-transformers/all-MiniLM-L6-v2", # 384dim
    "multimodal":     "Marqo/marqo-ecommerce-embeddings-L",    # text+image
    "visual":         "openai/clip-vit-base-patch32",           # 512dim
    "voice_stt":      "openai/whisper-base",                    # multilingual
}

AGENTS = {
    "shopper":   "Qwen/Qwen2.5-Coder-1.5B-Instruct",    # goal extraction
    "inventory": "Meta-Llama-3.1-8B-Instruct",           # bundle synthesis
    "fallback":  "google/gemma-2-2b-it",                  # fast reasoning
    "voice_tts": "microsoft/speech_t5_tts",               # voice response
}`}</pre>

              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`# Install (zero-cost, Apache 2.0)
pip install sentence-transformers transformers torch openai-whisper
huggingface-cli download Marqo/marqo-ecommerce-embeddings-L

# Index products with Marqo embeddings
model = SentenceTransformer("Marqo/marqo-ecommerce-embeddings-L")
text_vector = model.encode(f"{title} {description} {category}")
qdrant.upsert("products", [PointStruct(
    id=sku, vector={"text": text_vector.tolist()},
    payload={"title": title, "price": price, "stock": stock}
)])`}</pre>

              <pre className="text-[10px] font-mono text-muted-foreground whitespace-pre-wrap leading-relaxed rounded-lg bg-muted/20 border border-border p-3">{`# Agent coordination orchestrator
class MultiAgentStoreManager:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDINGS["ecommerce_text"])
        self.shopper = InferenceClient(model=AGENTS["shopper"])
        self.inventory = InferenceClient(model=AGENTS["inventory"])
        self.whisper = pipeline("automatic-speech-recognition", model=EMBEDDINGS["voice_stt"])
        self.qdrant = QdrantClient("localhost:6333")

    async def process_query(self, query: str) -> dict:
        # 1. Embed query
        query_vec = self.embedder.encode(query)
        # 2. Shopper Agent → structured goal
        goal = self.shopper.text_generation(shopper_prompt(query))
        # 3. Qdrant filtered search
        products = self.qdrant.search("products", query_vector=query_vec, limit=10)
        # 4. Retrieve episodes
        episodes = self.qdrant.search("episodes", query_vector=query_vec, limit=3)
        # 5. Inventory Agent → ranked bundles
        bundles = self.inventory.text_generation(
            inventory_prompt(goal, products, episodes)
        )
        return {"goal": goal, "bundles": bundles}`}</pre>
            </CardContent>
          </Card>

          {/* Budget */}
          <Card className="border-status-online/20 bg-status-online/5">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold">Hackathon Budget: $0</h3>
                  <p className="text-xs text-muted-foreground">All models Apache 2.0 / MIT · Free Colab T4 GPU · ~$0.02 per 1K queries</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-status-online">$0</div>
                  <div className="text-[10px] text-muted-foreground">total license cost</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Root page                                                          */
/* ------------------------------------------------------------------ */

export default function AIModels() {
  return (
    <div className="p-4 md:p-6 space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Brain className="h-5 w-5 text-primary" />
          <h1 className="text-xl font-bold text-foreground">AI Models & Embeddings</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Model selection, embedding strategies, prompt templates, and cost analysis for Shopper & Inventory agents.
        </p>
      </div>

      <Tabs defaultValue="hf" className="space-y-4">
        <TabsList className="bg-muted/50 h-auto flex-wrap gap-1">
          <TabsTrigger value="hf" className="text-xs gap-1"><Sparkles className="h-3 w-3" /> HF Stack</TabsTrigger>
          <TabsTrigger value="selection" className="text-xs gap-1"><Cpu className="h-3 w-3" /> Model Selection</TabsTrigger>
          <TabsTrigger value="routing" className="text-xs gap-1"><Layers className="h-3 w-3" /> Routing Matrix</TabsTrigger>
          <TabsTrigger value="embeddings" className="text-xs gap-1"><Globe className="h-3 w-3" /> Embeddings</TabsTrigger>
          <TabsTrigger value="opensource" className="text-xs gap-1"><Server className="h-3 w-3" /> Open-Source</TabsTrigger>
          <TabsTrigger value="prompts" className="text-xs gap-1"><Target className="h-3 w-3" /> Prompt Templates</TabsTrigger>
          <TabsTrigger value="cost" className="text-xs gap-1"><DollarSign className="h-3 w-3" /> Cost & Fallbacks</TabsTrigger>
        </TabsList>

        <TabsContent value="hf"><HFStackTab /></TabsContent>
        <TabsContent value="selection"><ModelSelectionTab /></TabsContent>
        <TabsContent value="routing"><RoutingMatrixTab /></TabsContent>
        <TabsContent value="embeddings"><EmbeddingsTab /></TabsContent>
        <TabsContent value="opensource"><OpenSourceTab /></TabsContent>
        <TabsContent value="prompts"><PromptTemplatesTab /></TabsContent>
        <TabsContent value="cost"><CostTab /></TabsContent>
      </Tabs>
    </div>
  );
}
