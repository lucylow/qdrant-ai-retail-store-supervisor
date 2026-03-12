import { useState, useCallback } from "react";
import {
  ArrowDown, ArrowRight, Database, Bot, Brain, Zap, Layers,
  CheckCircle2, XCircle, RotateCcw, BookOpen, GitBranch,
  Play, Search, FileText, Cpu, Network, Filter, Sparkles,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

/* ------------------------------------------------------------------ */
/*  Data                                                               */
/* ------------------------------------------------------------------ */

const RAG_MODES = [
  {
    id: "naive",
    label: "Naive RAG",
    tagline: "Linear retrieve → generate",
    color: "text-muted-foreground",
    badge: "bg-muted text-muted-foreground",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Retrieve Top-K from Qdrant", icon: Database },
      { label: "Compose Prompt", icon: FileText },
      { label: "Generate Answer", icon: Zap },
    ],
    pros: ["Simple to implement", "Low latency", "Predictable"],
    cons: ["No error recovery", "No learning", "Single-pass only"],
    latency: "~120ms",
    accuracy: "72%",
  },
  {
    id: "agentic",
    label: "Agentic RAG",
    tagline: "LLM agent with Shopper + Inventory tools",
    color: "text-primary",
    badge: "bg-primary/15 text-primary",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Shopper: Parse Goal", icon: Search },
      { label: "Retrieve (MMR) from Qdrant", icon: Database },
      { label: "Inventory: Solve Bundle", icon: Layers },
      { label: "Confidence Gate", icon: Filter },
      { label: "Re-retrieve if low confidence", icon: RotateCcw },
      { label: "Generate + Trace", icon: Zap },
    ],
    pros: ["Multi-agent coordination", "Confidence gating", "Episodic learning"],
    cons: ["More complex", "Higher latency on miss", "More moving parts"],
    latency: "~42ms (cache) / 2.4s",
    accuracy: "94%",
  },
  {
    id: "hybrid",
    label: "Hybrid RAG",
    tagline: "Query rewriting + retrieval validation",
    color: "text-accent",
    badge: "bg-accent/15 text-accent",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Rewrite / Expand Query", icon: RotateCcw },
      { label: "Retrieve from Qdrant", icon: Database },
      { label: "Validate Relevance (score > 0.65)", icon: Filter },
      { label: "Generate with validated docs", icon: Zap },
    ],
    pros: ["Better retrieval quality", "Filters noise", "Balanced complexity"],
    cons: ["Added latency from rewriting", "May over-filter"],
    latency: "~85ms",
    accuracy: "88%",
  },
  {
    id: "graph",
    label: "GraphRAG",
    tagline: "Knowledge graph + vector retrieval",
    color: "text-status-warning",
    badge: "bg-status-warning/15 text-status-warning",
    steps: [
      { label: "User Query", icon: Bot },
      { label: "Vector Retrieval", icon: Database },
      { label: "Extract Entities", icon: Brain },
      { label: "Knowledge Graph Traversal", icon: Network },
      { label: "Merge Vector + Graph Docs", icon: GitBranch },
      { label: "Generate with enriched context", icon: Zap },
    ],
    pros: ["Captures relationships", "Richer context", "Better for complex queries"],
    cons: ["Requires graph infrastructure", "Highest complexity", "Graph maintenance"],
    latency: "~150ms",
    accuracy: "91%",
  },
];

const LANGCHAIN_COMPONENTS = [
  { name: "Document Loaders", desc: "PDFs, CSVs, webpages → raw text", icon: FileText, color: "text-primary" },
  { name: "Text Splitters", desc: "Chunk documents for granular search", icon: Layers, color: "text-accent" },
  { name: "Embeddings", desc: "all-MiniLM-L6-v2 → 384-dim vectors", icon: Cpu, color: "text-status-warning" },
  { name: "Vector Store", desc: "Qdrant — cosine similarity search", icon: Database, color: "text-status-info" },
  { name: "Retriever", desc: "MMR / similarity search with filters", icon: Search, color: "text-primary" },
  { name: "Agent Tools", desc: "Shopper + Inventory as callable tools", icon: Bot, color: "text-accent" },
];

const TOOL_DEFINITIONS = [
  {
    name: "ShopperParseAndWrite",
    description: "Parses shopper text into a structured goal and writes it to the goals collection.",
    input: "user_message: str",
    output: "Parsed goal dict → upserted to Qdrant",
    color: "border-primary/25 bg-primary/5",
  },
  {
    name: "InventorySolve",
    description: "Retrieve products matching a goal and propose a bundle solution.",
    input: "goal_text: str",
    output: "Bundle candidates → upserted to solutions",
    color: "border-accent/25 bg-accent/5",
  },
];

interface SimStep {
  label: string;
  latency: number;
  done: boolean;
  active: boolean;
}

/* ------------------------------------------------------------------ */
/*  Flow Diagram                                                       */
/* ------------------------------------------------------------------ */

function PipelineFlow({ steps, modeColor }: { steps: typeof RAG_MODES[0]["steps"]; modeColor: string }) {
  const [activeStep, setActiveStep] = useState(-1);

  const animate = () => {
    let i = 0;
    setActiveStep(0);
    const interval = setInterval(() => {
      i++;
      if (i >= steps.length) {
        clearInterval(interval);
        setTimeout(() => setActiveStep(-1), 1000);
      } else {
        setActiveStep(i);
      }
    }, 450);
  };

  return (
    <div className="space-y-3">
      <Button size="sm" variant="outline" onClick={animate} className="gap-1.5 text-xs">
        <Play className="w-3 h-3" /> Animate
      </Button>
      <div className="flex flex-col gap-1">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const active = idx === activeStep;
          const done = activeStep > idx;
          return (
            <div key={step.label}>
              <div
                className={`flex items-center gap-3 px-3 py-2 rounded-lg border transition-all duration-300 ${
                  active
                    ? "border-primary bg-primary/10 scale-[1.02] shadow-md"
                    : done
                    ? "border-status-online/30 bg-status-online/5 opacity-70"
                    : "border-border bg-card"
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${active ? "text-primary" : modeColor}`} />
                <span className="text-sm flex-1">{step.label}</span>
                {done && <CheckCircle2 className="w-3.5 h-3.5 text-status-online" />}
                {active && (
                  <span className="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                )}
              </div>
              {idx < steps.length - 1 && (
                <div className="flex justify-center py-0.5">
                  <ArrowDown className="w-3 h-3 text-muted-foreground/40" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function LangChainRAGPage() {
  const [selectedMode, setSelectedMode] = useState("agentic");
  const activeMode = RAG_MODES.find((m) => m.id === selectedMode)!;

  return (
    <div className="p-6 space-y-8 animate-fade-in max-w-6xl mx-auto">
      {/* Header */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          LangChain + Qdrant · Context RAG
        </div>
        <h1 className="text-3xl font-bold tracking-tight">LangChain RAG Architecture</h1>
        <p className="text-muted-foreground max-w-2xl">
          Four RAG architectures mapped onto the Multi-Agent Store Manager — from Naive retrieval
          to Agentic tool-calling with Shopper + Inventory agents powered by Qdrant.
        </p>
      </div>

      <Tabs defaultValue="architectures" className="space-y-6">
        <TabsList className="bg-muted/50">
          <TabsTrigger value="architectures">Architectures</TabsTrigger>
          <TabsTrigger value="components">LangChain Stack</TabsTrigger>
          <TabsTrigger value="tools">Agent Tools</TabsTrigger>
          <TabsTrigger value="indexing">Indexing Pipeline</TabsTrigger>
        </TabsList>

        {/* --- Architectures --- */}
        <TabsContent value="architectures" className="space-y-6">
          {/* Mode selector */}
          <div className="flex flex-wrap gap-2">
            {RAG_MODES.map((mode) => (
              <button
                key={mode.id}
                onClick={() => setSelectedMode(mode.id)}
                className={`px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
                  selectedMode === mode.id
                    ? `${mode.badge} border-current`
                    : "border-border text-muted-foreground hover:text-foreground hover:border-border"
                }`}
              >
                {mode.label}
              </button>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Flow diagram */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <Badge className={activeMode.badge}>{activeMode.label}</Badge>
                  <span className="text-muted-foreground text-sm font-normal">{activeMode.tagline}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <PipelineFlow steps={activeMode.steps} modeColor={activeMode.color} />
              </CardContent>
            </Card>

            {/* Details */}
            <div className="space-y-4">
              {/* Metrics */}
              <Card>
                <CardContent className="pt-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <div className="text-lg font-bold font-mono text-primary">{activeMode.latency}</div>
                      <div className="text-xs text-muted-foreground">Latency</div>
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3 text-center">
                      <div className="text-lg font-bold font-mono text-status-online">{activeMode.accuracy}</div>
                      <div className="text-xs text-muted-foreground">Accuracy</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Pros */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-status-online" /> Strengths
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {activeMode.pros.map((p) => (
                      <li key={p} className="flex items-center gap-2 text-sm">
                        <ArrowRight className="w-3 h-3 text-status-online shrink-0" /> {p}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {/* Cons */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-1.5">
                    <XCircle className="w-3.5 h-3.5 text-destructive" /> Tradeoffs
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {activeMode.cons.map((c) => (
                      <li key={c} className="flex items-center gap-2 text-sm text-muted-foreground">
                        <ArrowRight className="w-3 h-3 text-destructive shrink-0" /> {c}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Comparison bar chart */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Architecture Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {RAG_MODES.map((mode) => {
                  const accuracy = parseInt(mode.accuracy);
                  return (
                    <div key={mode.id} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className={`font-medium ${mode.color}`}>{mode.label}</span>
                        <span className="text-muted-foreground">{mode.accuracy} accuracy · {mode.latency}</span>
                      </div>
                      <Progress value={accuracy} className="h-2" />
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- LangChain Stack --- */}
        <TabsContent value="components">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {LANGCHAIN_COMPONENTS.map((comp) => {
              const Icon = comp.icon;
              return (
                <Card key={comp.name} className="hover:border-primary/30 transition-colors">
                  <CardContent className="pt-4 space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
                        <Icon className={`w-4 h-4 ${comp.color}`} />
                      </div>
                      <h3 className="font-semibold text-sm">{comp.name}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground">{comp.desc}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Indexing flow */}
          <Card className="mt-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">LangChain → Qdrant Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap items-center gap-2 text-sm">
                {["Document Loaders", "Text Splitters", "Embeddings", "QdrantVectorStore", "Retriever", "Agent"].map(
                  (step, i) => (
                    <div key={step} className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {step}
                      </Badge>
                      {i < 5 && <ArrowRight className="w-3 h-3 text-muted-foreground" />}
                    </div>
                  )
                )}
              </div>
            </CardContent>
          </Card>

          {/* Code snippet */}
          <Card className="mt-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Quick Start</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-xs bg-muted/50 rounded-lg p-4 overflow-x-auto font-mono text-muted-foreground leading-relaxed">
{`from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# Attach to Qdrant
client = QdrantClient(url="localhost:6333")
vectorstore = QdrantVectorStore(
    client=client,
    collection_name="products",
    embedding=OpenAIEmbeddings()
)

# Create retriever (MMR for diversity)
retriever = vectorstore.as_retriever(
    search_type="mmr", search_kwargs={"k": 5}
)

# Use in agent pipeline
docs = retriever.get_relevant_documents(
    "2-person tent under 200CHF"
)`}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- Agent Tools --- */}
        <TabsContent value="tools" className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            {TOOL_DEFINITIONS.map((tool) => (
              <Card key={tool.name} className={`border ${tool.color}`}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Bot className="w-4 h-4" />
                    {tool.name}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">{tool.description}</p>
                  <div className="space-y-1.5 text-xs">
                    <div className="flex gap-2">
                      <span className="text-muted-foreground w-12 shrink-0">Input:</span>
                      <code className="font-mono bg-muted/50 px-1.5 py-0.5 rounded">{tool.input}</code>
                    </div>
                    <div className="flex gap-2">
                      <span className="text-muted-foreground w-12 shrink-0">Output:</span>
                      <span>{tool.output}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Agent decision flow */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Brain className="w-4 h-4 text-primary" />
                Coordinator Agent Decision Flow
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {[
                  { condition: "User intent unclear", action: "→ Call Shopper to parse & clarify" },
                  { condition: "Goal parsed, need products", action: "→ Call Inventory to search & bundle" },
                  { condition: "Low confidence (<70%)", action: "→ Re-retrieve with expanded query" },
                  { condition: "Bundle ready", action: "→ Present to user, capture outcome" },
                  { condition: "Outcome received", action: "→ Write episodic memory for future reuse" },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3 px-3 py-2 rounded-lg bg-card border border-border">
                    <Badge variant="outline" className="text-xs shrink-0 mt-0.5">
                      {i + 1}
                    </Badge>
                    <div>
                      <span className="font-medium">{item.condition}</span>
                      <span className="text-muted-foreground"> {item.action}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Production tips */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Production Tips</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5 text-sm text-muted-foreground">
                {[
                  "Use as_retriever(search_type='mmr') to avoid near-duplicate chunks",
                  "Give each tool conservative responsibility (Shopper writes goals only)",
                  "Use confidence thresholds to decide when to escalate to human",
                  "Cheap models for parsing, expensive models for planning/ranking",
                  "Keep product stock fresh — vector similarity won't catch staleness",
                ].map((tip) => (
                  <li key={tip} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-status-online shrink-0 mt-0.5" />
                    {tip}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- Indexing Pipeline --- */}
        <TabsContent value="indexing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Indexing Pipeline (Data Ingestion)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  { step: "1. Load Documents", desc: "PDFs, CSVs, product catalogs → raw text via LangChain loaders", icon: FileText },
                  { step: "2. Split Text", desc: "RecursiveCharacterTextSplitter(chunk_size=500, overlap=50)", icon: Layers },
                  { step: "3. Embed Chunks", desc: "all-MiniLM-L6-v2 → 384-dim vectors (or OpenAI 1536-dim)", icon: Cpu },
                  { step: "4. Store in Qdrant", desc: "QdrantVectorStore.from_documents() with payload indexes", icon: Database },
                  { step: "5. Create Retriever", desc: "vectorstore.as_retriever(search_type='mmr', k=5)", icon: Search },
                ].map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.step}>
                      <div className="flex items-start gap-3 px-4 py-3 rounded-lg border border-border bg-card">
                        <Icon className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <div>
                          <div className="font-medium text-sm">{item.step}</div>
                          <div className="text-xs text-muted-foreground">{item.desc}</div>
                        </div>
                      </div>
                      {i < 4 && (
                        <div className="flex justify-center py-0.5">
                          <ArrowDown className="w-3 h-3 text-muted-foreground/40" />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Collections */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Database className="w-4 h-4 text-accent" />
                Qdrant Collections
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {["goals", "products", "solutions", "episodes", "promotions"].map((col) => (
                  <div key={col} className="rounded-lg border border-accent/20 bg-accent/5 p-3 text-center">
                    <Database className="w-4 h-4 text-accent mx-auto mb-1" />
                    <div className="text-sm font-medium capitalize">{col}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
