"use client";

import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { DashboardSidebarNav } from "@/components/dashboard-sidebar-nav";

export function DashboardShellClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!sidebarOpen) {
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [sidebarOpen]);

  return (
    <div className="flex min-h-0 flex-1">
      <aside className="hidden w-56 shrink-0 flex-col border-r border-on-surface/5 bg-surface-container-low lg:flex">
        <div className="border-b border-on-surface/5 px-4 py-4">
          <p className="text-xs font-semibold text-on-surface-variant">研究</p>
          <p className="mt-0.5 text-sm font-semibold text-on-surface">
            Terminal <span className="text-primary-container">v2.0</span>
          </p>
        </div>
        <DashboardSidebarNav />
      </aside>

      {sidebarOpen ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            aria-label="关闭导航"
            className="absolute inset-0 bg-black/60"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="relative flex h-full w-[min(18rem,88vw)] flex-col border-r border-on-surface/10 bg-surface-container-low shadow-xl">
            <div className="flex items-center justify-between border-b border-on-surface/5 px-4 py-4">
              <div>
                <p className="text-xs font-semibold text-on-surface-variant">
                  研究
                </p>
                <p className="mt-0.5 text-sm font-semibold text-on-surface">
                  Terminal <span className="text-primary-container">v2.0</span>
                </p>
              </div>
              <button
                type="button"
                aria-label="关闭菜单"
                className="rounded-md p-2 text-on-surface-variant transition hover:bg-surface-container-highest hover:text-on-surface"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <DashboardSidebarNav onNavigate={() => setSidebarOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center gap-3 border-b border-on-surface/5 px-4 py-2.5 lg:hidden">
          <button
            type="button"
            aria-label="打开导航菜单"
            className="rounded-md p-2 text-on-surface-variant transition hover:bg-surface-container-highest hover:text-on-surface"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </button>
          <p className="text-sm font-semibold text-on-surface">
            研究 Terminal{" "}
            <span className="text-primary-container">v2.0</span>
          </p>
        </div>
        <main className="min-w-0 flex-1 overflow-auto p-4 sm:p-5 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
