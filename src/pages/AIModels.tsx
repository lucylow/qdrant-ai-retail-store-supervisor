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
  Database, Target, Activity, Sparkles, Server
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

      <Tabs defaultValue="selection" className="space-y-4">
        <TabsList className="bg-muted/50 h-auto flex-wrap gap-1">
          <TabsTrigger value="selection" className="text-xs gap-1"><Cpu className="h-3 w-3" /> Model Selection</TabsTrigger>
          <TabsTrigger value="routing" className="text-xs gap-1"><Layers className="h-3 w-3" /> Routing Matrix</TabsTrigger>
          <TabsTrigger value="embeddings" className="text-xs gap-1"><Globe className="h-3 w-3" /> Embeddings</TabsTrigger>
          <TabsTrigger value="opensource" className="text-xs gap-1"><Server className="h-3 w-3" /> Open-Source</TabsTrigger>
          <TabsTrigger value="prompts" className="text-xs gap-1"><Target className="h-3 w-3" /> Prompt Templates</TabsTrigger>
          <TabsTrigger value="cost" className="text-xs gap-1"><DollarSign className="h-3 w-3" /> Cost & Fallbacks</TabsTrigger>
        </TabsList>

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
