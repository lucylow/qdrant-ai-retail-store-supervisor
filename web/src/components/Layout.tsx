import { Outlet } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { MobileBottomNav } from "@/components/MobileBottomNav";
import { Breadcrumbs } from "@/components/Breadcrumbs";

export function Layout() {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-h-screen overflow-x-hidden">
          <header className="h-12 flex items-center border-b border-border px-3 gap-3 shrink-0">
            <SidebarTrigger className="shrink-0" />
            <Breadcrumbs />
          </header>
          <main className="flex-1 pb-16 md:pb-0">
            <Outlet />
          </main>
        </div>
        <MobileBottomNav />
      </div>
    </SidebarProvider>
  );
}
