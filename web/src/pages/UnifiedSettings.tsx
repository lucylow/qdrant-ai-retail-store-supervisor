import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSearchParams } from "react-router-dom";

import GDPRPage from "./GDPR";
import DatasetsPage from "./Datasets";
import QdrantCloudPage from "./QdrantCloud";

const SETTINGS_TABS = [
  { id: "general", label: "General" },
  { id: "gdpr", label: "GDPR & Privacy" },
  { id: "datasets", label: "Datasets" },
  { id: "qdrant-cloud", label: "Qdrant Cloud" },
] as const;

export default function UnifiedSettings() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") || "general";

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <Tabs value={activeTab} onValueChange={(t) => setSearchParams({ tab: t })} className="flex flex-col flex-1 min-h-0">
        <div className="border-b border-border px-4 pt-4 pb-0 shrink-0">
          <h1 className="text-xl font-bold mb-3">Settings</h1>
          <TabsList className="bg-muted/50">
            {SETTINGS_TABS.map((tab) => (
              <TabsTrigger key={tab.id} value={tab.id} className="text-xs">
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        <div className="flex-1 overflow-y-auto">
          <TabsContent value="general" className="mt-0">
            <div className="p-6 space-y-4">
              <h2 className="text-lg font-semibold">General Settings</h2>
              <p className="text-sm text-muted-foreground">
                Application preferences and configuration.
              </p>
              <div className="rounded-xl border border-border bg-card p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Theme</span>
                  <span className="text-sm text-muted-foreground">System default</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Embedding Model</span>
                  <span className="text-sm text-muted-foreground font-mono">all-MiniLM-L6-v2</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">LLM Model</span>
                  <span className="text-sm text-muted-foreground font-mono">gpt-4.1-mini</span>
                </div>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="gdpr" className="mt-0">
            <GDPRPage />
          </TabsContent>
          <TabsContent value="datasets" className="mt-0">
            <DatasetsPage />
          </TabsContent>
          <TabsContent value="qdrant-cloud" className="mt-0">
            <QdrantCloudPage />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
