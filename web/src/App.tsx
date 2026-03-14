import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Layout } from "@/components/Layout";
import Index from "./pages/Index";
import ChatPage from "./pages/Chat";
import UnifiedDashboard from "./pages/UnifiedDashboard";
import UnifiedSettings from "./pages/UnifiedSettings";
import VisualSearch from "./pages/VisualSearch";
import LiveMapPage from "./pages/LiveMap";
import StoreMapPage from "./pages/StoreMap";
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
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/dashboard" element={<UnifiedDashboard />} />
            <Route path="/visual-search" element={<VisualSearch />} />
            <Route path="/livemap" element={<LiveMapPage />} />
            <Route path="/store-map" element={<StoreMapPage />} />
            <Route path="/settings" element={<UnifiedSettings />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
