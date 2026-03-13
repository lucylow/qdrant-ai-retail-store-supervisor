import { Home, MessageSquare, BarChart3, Settings, Database, Map, MapPin } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: Home },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { to: "/livemap", label: "LiveMap", icon: Map },
  { to: "/store-map", label: "Store map", icon: MapPin },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();

  const isActive = (path: string) =>
    path === "/" ? location.pathname === "/" : location.pathname.startsWith(path);

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border px-3 py-3">
        <div className="flex items-center gap-2 min-w-0">
          <Database className="w-5 h-5 text-primary shrink-0" />
          {!collapsed && (
            <div className="min-w-0">
              <div className="text-sm font-bold text-sidebar-foreground truncate">
                Retail AI
              </div>
              <div className="text-[10px] text-sidebar-foreground/50 truncate">
                Store Supervisor
              </div>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {NAV_ITEMS.map((item) => (
                <SidebarMenuItem key={item.to}>
                  <SidebarMenuButton asChild isActive={isActive(item.to)}>
                    <NavLink
                      to={item.to}
                      end={item.to === "/"}
                      className="hover:bg-sidebar-accent/50"
                      activeClassName="bg-primary/15 text-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.label}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-3">
        {!collapsed && (
          <div className="text-[10px] text-sidebar-foreground/40">
            <div className="font-medium">GenAI Zurich 2026</div>
            <div>Qdrant Challenge</div>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
}
