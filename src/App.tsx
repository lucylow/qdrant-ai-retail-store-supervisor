import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Layout } from "@/components/Layout";
import Index from "./pages/Index";
import DashboardPage from "./pages/Dashboard";
import ChatPage from "./pages/Chat";
import GoalsPage from "./pages/Goals";
import EpisodesPage from "./pages/Episodes";
import ProductsPage from "./pages/Products";
import AgentsPage from "./pages/Agents";
import MetricsPage from "./pages/Metrics";
import ScalePage from "./pages/Scale";
import QdrantPage from "./pages/Qdrant";
import DemoPage from "./pages/Demo";
import HackathonPage from "./pages/Hackathon";
import SettingsPage from "./pages/Settings";
import SolutionsPage from "./pages/Solutions";
import EnterprisePage from "./pages/Enterprise";
import GenAIPage from "./pages/GenAI";
import EvolvePage from "./pages/Evolve";
import QdrantCloudPage from "./pages/QdrantCloud";
import DatasetsPage from "./pages/Datasets";
import GDPRPage from "./pages/GDPR";
import ArchitecturePage from "./pages/Architecture";
import RAGComparisonPage from "./pages/RAGComparison";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Index />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/goals" element={<GoalsPage />} />
            <Route path="/solutions/:goalId" element={<SolutionsPage />} />
            <Route path="/solutions" element={<SolutionsPage />} />
            <Route path="/episodes" element={<EpisodesPage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/metrics" element={<MetricsPage />} />
            <Route path="/scale" element={<ScalePage />} />
            <Route path="/qdrant" element={<QdrantPage />} />
            <Route path="/demo" element={<DemoPage />} />
            <Route path="/hackathon" element={<HackathonPage />} />
            <Route path="/enterprise" element={<EnterprisePage />} />
            <Route path="/genai" element={<GenAIPage />} />
            <Route path="/evolve" element={<EvolvePage />} />
            <Route path="/qdrant-cloud" element={<QdrantCloudPage />} />
            <Route path="/datasets" element={<DatasetsPage />} />
            <Route path="/gdpr" element={<GDPRPage />} />
            <Route path="/architecture" element={<ArchitecturePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
