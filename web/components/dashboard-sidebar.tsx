"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  HelpCircle,
  Layers,
  LineChart,
  Settings,
  Table2,
} from "lucide-react";
import { isNavChildActive, sidebarNavItems } from "@/lib/navigation";

const iconByLabel: Record<string, typeof Table2> = {
  基本面: Table2,
  技术图: LineChart,
  板块聚类: Layers,
  行业分析: BarChart3,
};

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-56 shrink-0 flex-col border-r border-on-surface/5 bg-surface-container-low">
      <div className="border-b border-on-surface/5 px-4 py-4">
        <p className="text-xs font-semibold text-on-surface-variant">
          研究
        </p>
        <p className="mt-0.5 text-sm font-semibold text-on-surface">
          Terminal <span className="text-primary-container">v2.0</span>
        </p>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {sidebarNavItems.map((item) => {
          const Icon = iconByLabel[item.label] || Table2;
          const active = item.match.test(pathname);
          const children = "children" in item ? item.children : undefined;

          return (
            <div key={item.href}>
              <Link
                href={item.href}
                className={`flex items-center gap-2.5 rounded-md px-3 py-2.5 text-sm transition ${
                  active
                    ? "bg-surface-bright text-on-surface shadow-[inset_0_0_0_1px_rgb(218_226_253/0.12)]"
                    : "text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface"
                }`}
              >
                <Icon
                  className={`h-4 w-4 shrink-0 ${active ? "text-primary-container" : ""}`}
                />
                {item.label}
              </Link>
              {children ? (
                <div className="mt-1 space-y-0.5 pl-6">
                  {children.map((child) => {
                    const childActive = isNavChildActive(pathname, child);

                    return (
                      <Link
                        key={child.href}
                        href={child.href}
                        className={`block rounded-md px-3 py-1.5 text-xs transition ${
                          childActive
                            ? "bg-surface-container-high text-on-surface"
                            : "text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface"
                        }`}
                      >
                        {child.label}
                      </Link>
                    );
                  })}
                </div>
              ) : null}
            </div>
          );
        })}
      </nav>

      <div className="space-y-0.5 border-t border-on-surface/5 p-3">
        <button
          type="button"
          className="flex w-full items-center gap-2.5 rounded-md px-3 py-2 text-sm text-on-surface-variant transition hover:bg-surface-container-highest hover:text-on-surface"
        >
          <Settings className="h-4 w-4" />
          设置
        </button>
        <button
          type="button"
          className="flex w-full items-center gap-2.5 rounded-md px-3 py-2 text-sm text-on-surface-variant transition hover:bg-surface-container-highest hover:text-on-surface"
        >
          <HelpCircle className="h-4 w-4" />
          支持
        </button>
      </div>
    </aside>
  );
}
