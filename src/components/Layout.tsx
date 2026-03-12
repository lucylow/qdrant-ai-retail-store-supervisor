import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";

export function Layout() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 ml-16 lg:ml-56 min-h-screen overflow-x-hidden transition-all duration-300">
        <Outlet />
      </main>
    </div>
  );
}
