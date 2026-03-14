import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSearchParams } from "react-router-dom";

// Lazy imports of all existing pages as tab content
import GoalsPage from "./Goals";
import EpisodesPage from "./Episodes";
import ProductsPage from "./Products";
import AgentsPage from "./Agents";
import MetricsPage from "./Metrics";
import QdrantPage from "./Qdrant";
import RAGComparisonPage from "./RAGComparison";
import SemanticCachePage from "./SemanticCache";
import LangChainRAGPage from "./LangChainRAG";
import AgenticAIPage from "./AgenticAI";
import AIAnalyticsPage from "./AIAnalytics";
import ArchitecturePage from "./Architecture";
import AnomalyDetectionPage from "./AnomalyDetection";
import QdrantCollectionsPage from "./QdrantCollections";
import RoutingOrchestrationPage from "./RoutingOrchestration";
import AIModelsPage from "./AIModels";
import MCPToolsPage from "./MCPTools";
import AdvancedSearchPage from "./AdvancedSearch";

const DASHBOARD_TABS = [
  { id: "overview", label: "Overview" },
  { id: "agents", label: "Agents" },
  { id: "routing", label: "Routing" },
  { id: "models", label: "AI Models" },
  { id: "search", label: "Advanced Search" },
  { id: "mcp", label: "MCP Tools" },
  { id: "goals", label: "Goals" },
  { id: "episodes", label: "Memory" },
  { id: "products", label: "Products" },
  { id: "metrics", label: "Metrics" },
  { id: "qdrant", label: "Qdrant" },
  { id: "collections", label: "Collections" },
  { id: "analytics", label: "Analytics" },
  { id: "anomaly", label: "Anomaly Detection" },
  { id: "rag", label: "RAG" },
  { id: "cache", label: "Cache" },
  { id: "langchain", label: "LangChain" },
  { id: "agentic", label: "Agentic AI" },
  { id: "architecture", label: "Architecture" },
] as const;

export default function UnifiedDashboard() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") || "overview";

  const setTab = (tab: string) => {
    setSearchParams({ tab });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <Tabs value={activeTab} onValueChange={setTab} className="flex flex-col flex-1 min-h-0">
        <div className="border-b border-border px-4 pt-4 pb-0 shrink-0">
          <h1 className="text-xl font-bold mb-3">Dashboard</h1>
          <TabsList className="bg-muted/50 h-auto flex-wrap gap-1 justify-start">
            {DASHBOARD_TABS.map((tab) => (
              <TabsTrigger key={tab.id} value={tab.id} className="text-xs">
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        <div className="flex-1 overflow-y-auto">
          <TabsContent value="overview" className="mt-0 h-full">
            <AIAnalyticsPage />
          </TabsContent>
          <TabsContent value="agents" className="mt-0">
            <AgentsPage />
          </TabsContent>
          <TabsContent value="routing" className="mt-0">
            <RoutingOrchestrationPage />
          </TabsContent>
          <TabsContent value="models" className="mt-0">
            <AIModelsPage />
          </TabsContent>
          <TabsContent value="search" className="mt-0">
            <AdvancedSearchPage />
          </TabsContent>
          <TabsContent value="mcp" className="mt-0">
            <MCPToolsPage />
          </TabsContent>
          <TabsContent value="goals" className="mt-0">
            <GoalsPage />
          </TabsContent>
          <TabsContent value="episodes" className="mt-0">
            <EpisodesPage />
          </TabsContent>
          <TabsContent value="products" className="mt-0">
            <ProductsPage />
          </TabsContent>
          <TabsContent value="metrics" className="mt-0">
            <MetricsPage />
          </TabsContent>
          <TabsContent value="qdrant" className="mt-0">
            <QdrantPage />
          </TabsContent>
          <TabsContent value="collections" className="mt-0">
            <QdrantCollectionsPage />
          </TabsContent>
          <TabsContent value="analytics" className="mt-0">
            <AIAnalyticsPage />
          </TabsContent>
          <TabsContent value="anomaly" className="mt-0">
            <AnomalyDetectionPage />
          </TabsContent>
          <TabsContent value="rag" className="mt-0">
            <RAGComparisonPage />
          </TabsContent>
          <TabsContent value="cache" className="mt-0">
            <SemanticCachePage />
          </TabsContent>
          <TabsContent value="langchain" className="mt-0">
            <LangChainRAGPage />
          </TabsContent>
          <TabsContent value="agentic" className="mt-0">
            <AgenticAIPage />
          </TabsContent>
          <TabsContent value="architecture" className="mt-0">
            <ArchitecturePage />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
