import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import MapLogistics from "@/components/MapLogistics";
import { LogisticsPanel } from "@/components/LogisticsPanel";

const DEFAULT_CENTER: [number, number] = [47.3769, 8.5417];

export function StoreMapPage() {
  const [center] = useState<[number, number]>(DEFAULT_CENTER);

  return (
    <div className="flex flex-col gap-4 p-4 h-full">
      <div className="grid grid-cols-1 lg:grid-cols-[1fr,340px] gap-4 h-full">
        <Card className="min-h-[480px] lg:min-h-[600px]">
          <CardHeader>
            <CardTitle>Migros stores – Map &amp; navigation</CardTitle>
          </CardHeader>
          <CardContent className="h-[420px] lg:h-[calc(100%-4rem)] p-0">
            <MapLogistics />
          </CardContent>
        </Card>
        <div className="space-y-4">
          <LogisticsPanel depot={{ lat: center[0], lon: center[1] }} />
        </div>
      </div>
    </div>
  );
}

export default StoreMapPage;
