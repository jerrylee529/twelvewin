"use client";

import { useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  ChevronRight,
  FileText,
  LineChart,
} from "lucide-react";

import { AgentMessageBody } from "@/components/agent-message-body";
import { parseAgentContent } from "@/lib/agent-message-content";
import { parseSummarySections } from "@/lib/agent-summary-sections";

function sectionIcon(title: string) {
  if (title.includes("风险") || title.includes("局限")) {
    return AlertTriangle;
  }
  if (title.includes("技术")) {
    return LineChart;
  }
  if (title.includes("基本面") || title.includes("估值") || title.includes("盈利")) {
    return BarChart3;
  }
  return FileText;
}

function SummarySectionCard({
  title,
  content,
  defaultExpanded = true,
}: {
  title: string;
  content: string;
  defaultExpanded?: boolean;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const Icon = sectionIcon(title);

  return (
    <article className="overflow-hidden rounded-sm border border-outline-variant/40 bg-surface-container-low/60">
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="flex w-full items-center gap-2 px-3 py-2.5 text-left transition hover:bg-surface-container-high/50"
        aria-expanded={expanded}
      >
        <ChevronRight
          className={`h-4 w-4 shrink-0 text-on-surface-variant transition-transform ${expanded ? "rotate-90" : ""}`}
        />
        <Icon className="h-4 w-4 shrink-0 text-primary-container" />
        <span className="text-sm font-semibold text-on-surface">{title}</span>
      </button>
      {expanded ? (
        <div className="border-t border-outline-variant/30 px-3 py-3">
          <AgentMessageBody content={content} />
        </div>
      ) : null}
    </article>
  );
}

export function AgentSummaryView({
  content,
  loading,
  error,
}: {
  content: string;
  loading?: boolean;
  error?: string | null;
}) {
  const { thinkBlocks, markdown } = useMemo(() => {
    const segments = parseAgentContent(content);
    const thinks = segments
      .filter((segment) => segment.type === "think")
      .map((segment) => segment.content);
    const md = segments
      .filter((segment) => segment.type === "markdown")
      .map((segment) => segment.content)
      .join("\n\n");
    return { thinkBlocks: thinks, markdown: md || content };
  }, [content]);

  const sections = useMemo(
    () => parseSummarySections(markdown),
    [markdown],
  );

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((item) => (
          <div
            key={item}
            className="h-20 animate-pulse rounded-sm border border-outline-variant/30 bg-surface-container-low/40"
          />
        ))}
        <p className="text-sm text-on-surface-variant">正在生成摘要…</p>
      </div>
    );
  }

  if (error) {
    return <p className="text-sm text-error">{error}</p>;
  }

  if (!content.trim()) {
    return <p className="text-sm text-on-surface-variant">暂无摘要。</p>;
  }

  return (
    <div className="space-y-3">
      {thinkBlocks.length > 0 ? (
        <details className="rounded-sm border border-outline-variant/35 bg-surface-container/80">
          <summary className="cursor-pointer px-3 py-2 text-xs font-medium text-on-surface-variant">
            思考过程（可展开）
          </summary>
          <pre className="max-h-40 overflow-y-auto border-t border-outline-variant/30 px-3 py-2 text-xs leading-6 whitespace-pre-wrap text-on-surface-variant">
            {thinkBlocks.join("\n\n")}
          </pre>
        </details>
      ) : null}

      {sections.length <= 1 ? (
        <div className="rounded-sm border border-outline-variant/40 bg-surface-container-low/60 p-3">
          <AgentMessageBody content={markdown} />
        </div>
      ) : (
        sections.map((section, index) => (
          <SummarySectionCard
            key={section.title}
            title={section.title}
            content={section.content}
            defaultExpanded={index === 0}
          />
        ))
      )}
    </div>
  );
}
