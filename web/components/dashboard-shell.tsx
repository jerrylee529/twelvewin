import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { DashboardShellClient } from "@/components/dashboard-shell-client";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-surface">
      <SiteHeader />
      <DashboardShellClient>{children}</DashboardShellClient>
    </div>
  );
}

export function PageHeader({
  title,
  description,
  updateTime,
  action,
  badge,
}: {
  title: string;
  description?: string;
  updateTime?: string | null;
  action?: React.ReactNode;
  badge?: React.ReactNode;
}) {
  return (
    <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <div className="mb-1 flex items-center gap-2">
          {badge}
          <p className="title-sm">数据终端</p>
        </div>
        <h1 className="text-lg font-semibold text-on-surface">{title}</h1>
        {description ? (
          <p className="mt-1 text-xs text-on-surface-variant">{description}</p>
        ) : null}
        {updateTime ? (
          <p className="mt-2 label-sm tabular-nums">数据截至 {updateTime}</p>
        ) : null}
      </div>
      {action}
    </div>
  );
}

export function EmptyState({
  message = "没有相关的匹配结果",
  hint,
}: {
  message?: string;
  hint?: string;
}) {
  return (
    <div className="terminal-pane-recessed px-6 py-14 text-center">
      <p className="text-sm font-medium text-on-surface">{message}</p>
      {hint ? (
        <p className="mt-2 text-xs text-on-surface-variant">{hint}</p>
      ) : null}
    </div>
  );
}

export function StockLink({
  code,
  name,
}: {
  code: string;
  name?: string | null;
}) {
  return (
    <Link
      href={`/stock/${code}`}
      className="font-medium text-on-surface hover:text-primary-container"
    >
      {name || code}
    </Link>
  );
}
