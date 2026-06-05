"use client";

import { useMemo, useState } from "react";
import { ChevronRight } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

import {
  parseAgentContent,
  type AgentContentSegment,
} from "@/lib/agent-message-content";

function ThinkBlock({
  content,
  complete,
  defaultExpanded = false,
}: {
  content: string;
  complete: boolean;
  defaultExpanded?: boolean;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div className="mb-3 rounded-sm border border-outline-variant/35 bg-surface-container/80">
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs text-on-surface-variant transition hover:text-on-surface"
        aria-expanded={expanded}
      >
        <ChevronRight
          className={`h-3.5 w-3.5 shrink-0 transition-transform ${expanded ? "rotate-90" : ""}`}
          aria-hidden
        />
        <span className="font-medium text-on-surface">思考过程</span>
        <span className="text-[10px] uppercase tracking-[0.14em] text-on-surface-variant">
          {complete ? "可展开" : "生成中…"}
        </span>
      </button>
      {expanded ? (
        <pre className="max-h-48 overflow-y-auto overscroll-contain border-t border-outline-variant/30 px-3 py-2 text-xs leading-6 whitespace-pre-wrap text-on-surface-variant">
          {content}
        </pre>
      ) : null}
    </div>
  );
}

function MarkdownBlock({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeSanitize]}
      components={{
        h1: ({ children }) => (
          <h4 className="mt-4 mb-2 text-sm font-semibold text-on-surface first:mt-0">
            {children}
          </h4>
        ),
        h2: ({ children }) => (
          <h4 className="mt-4 mb-2 text-sm font-semibold text-on-surface first:mt-0">
            {children}
          </h4>
        ),
        h3: ({ children }) => (
          <h4 className="mt-3 mb-1.5 text-sm font-semibold text-on-surface first:mt-0">
            {children}
          </h4>
        ),
        p: ({ children }) => (
          <p className="mb-2 text-sm leading-7 text-on-surface last:mb-0">
            {children}
          </p>
        ),
        ul: ({ children }) => (
          <ul className="mb-2 list-disc space-y-1 pl-5 text-sm leading-7 text-on-surface">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="mb-2 list-decimal space-y-1 pl-5 text-sm leading-7 text-on-surface">
            {children}
          </ol>
        ),
        li: ({ children }) => <li className="text-on-surface">{children}</li>,
        strong: ({ children }) => (
          <strong className="font-semibold text-on-surface">{children}</strong>
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-container underline-offset-2 hover:underline"
          >
            {children}
          </a>
        ),
        code: ({ children }) => (
          <code className="rounded-sm bg-surface-container-high px-1 py-0.5 font-mono text-xs text-on-surface">
            {children}
          </code>
        ),
        pre: ({ children }) => (
          <pre className="mb-2 overflow-x-auto rounded-sm border border-outline-variant/30 bg-surface-container-high p-3 font-mono text-xs leading-6 text-on-surface">
            {children}
          </pre>
        ),
        hr: () => <hr className="my-3 border-outline-variant/40" />,
        table: ({ children }) => (
          <div className="mb-2 overflow-x-auto">
            <table className="w-full border-collapse text-left text-xs text-on-surface">
              {children}
            </table>
          </div>
        ),
        th: ({ children }) => (
          <th className="border border-outline-variant/40 bg-surface-container-high px-2 py-1 font-semibold">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="border border-outline-variant/30 px-2 py-1">
            {children}
          </td>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

function SegmentList({ segments }: { segments: AgentContentSegment[] }) {
  if (segments.length === 0) {
    return null;
  }

  return (
    <>
      {segments.map((segment, index) =>
        segment.type === "think" ? (
          <ThinkBlock
            key={`think-${index}`}
            content={segment.content}
            complete={segment.complete}
          />
        ) : (
          <div key={`md-${index}`} className="agent-markdown">
            <MarkdownBlock content={segment.content} />
          </div>
        ),
      )}
    </>
  );
}

export function AgentMessageBody({
  content,
  className = "",
  fallback = "…",
}: {
  content: string;
  className?: string;
  fallback?: string;
}) {
  const segments = useMemo(() => parseAgentContent(content), [content]);

  if (!content.trim()) {
    return (
      <p className={`text-sm text-on-surface-variant ${className}`.trim()}>
        {fallback}
      </p>
    );
  }

  if (segments.length === 0) {
    return (
      <div className={`agent-markdown ${className}`.trim()}>
        <MarkdownBlock content={content} />
      </div>
    );
  }

  return (
    <div className={className}>
      <SegmentList segments={segments} />
    </div>
  );
}
