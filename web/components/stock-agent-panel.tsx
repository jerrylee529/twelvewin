"use client";

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";

import { AgentMessageBody } from "@/components/agent-message-body";
import { useStockQuote } from "@/components/stock-quote-provider";

type AgentStatus = {
  enabled: boolean;
  summaryMode: "workflow" | "chat";
  missing?: string[];
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const QUICK_PROMPTS = [
  "相对同行业，估值处于什么水平？",
  "近期有哪些技术信号？",
  "ROE 和盈利趋势如何？",
];

const PANEL_SECTION_CLASS =
  "mt-2 flex min-h-0 flex-col border-t border-outline-variant/40 pt-8 lg:mt-0 lg:flex-1 lg:min-h-0 lg:overflow-hidden lg:border-t-0 lg:pt-0";

const CHAT_SCROLL_STICKY_THRESHOLD_PX = 80;

function extractAnswerFromBlockingPayload(payload: Record<string, unknown>): string {
  if (typeof payload.answer === "string") {
    return payload.answer;
  }

  const data = payload.data;
  if (data && typeof data === "object") {
    const outputs = (data as { outputs?: Record<string, unknown> }).outputs;
    if (outputs) {
      for (const value of Object.values(outputs)) {
        if (typeof value === "string" && value.trim()) {
          return value;
        }
      }
    }
  }

  return "";
}

async function readSseStream(
  response: Response,
  onChunk: (text: string) => void,
): Promise<{ conversationId?: string }> {
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Missing response stream.");
  }

  const decoder = new TextDecoder();
  let buffer = "";
  let conversationId: string | undefined;

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith("data:")) {
        continue;
      }

      const payloadText = trimmed.slice(5).trim();
      if (!payloadText || payloadText === "[DONE]") {
        continue;
      }

      try {
        const payload = JSON.parse(payloadText) as Record<string, unknown>;
        if (typeof payload.conversation_id === "string") {
          conversationId = payload.conversation_id;
        }

        const event = payload.event;
        if (event === "message" || event === "agent_message") {
          const answer = payload.answer;
          if (typeof answer === "string" && answer) {
            onChunk(answer);
          }
        }
      } catch {
        // Ignore malformed SSE chunks.
      }
    }
  }

  return { conversationId };
}

export function StockAgentPanel({ code }: { code: string }) {
  const { data: quoteData } = useStockQuote();
  const stockName = quoteData?.quot?.name || code;

  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState("");
  const messagesScrollRef = useRef<HTMLDivElement | null>(null);
  const prevMessageCountRef = useRef(0);

  const agentInputs = useMemo(
    () => ({
      stock_code: code,
      stock_name: stockName,
      locale: "zh-CN",
    }),
    [code, stockName],
  );

  useEffect(() => {
    let cancelled = false;

    async function loadStatus() {
      try {
        const response = await fetch("/api/agent", { cache: "no-store" });
        if (!response.ok) {
          return;
        }
        const payload = (await response.json()) as AgentStatus;
        if (!cancelled) {
          setStatus(payload);
        }
      } catch {
        if (!cancelled) {
          setStatus({ enabled: false, summaryMode: "chat" });
        }
      }
    }

    void loadStatus();
    return () => {
      cancelled = true;
    };
  }, []);

  const loadSummary = useCallback(async () => {
    setSummaryLoading(true);
    setSummaryError(null);

    try {
      const response = await fetch("/api/agent/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ inputs: agentInputs }),
      });

      const payload = (await response.json()) as Record<string, unknown>;
      if (!response.ok) {
        throw new Error(
          typeof payload.error === "string"
            ? payload.error
            : "Failed to load AI summary.",
        );
      }

      setSummary(extractAnswerFromBlockingPayload(payload));
    } catch (error) {
      setSummaryError(
        error instanceof Error ? error.message : "Failed to load AI summary.",
      );
    } finally {
      setSummaryLoading(false);
    }
  }, [agentInputs]);

  useEffect(() => {
    if (!status?.enabled) {
      return;
    }
    void loadSummary();
  }, [loadSummary, status?.enabled]);

  useEffect(() => {
    const scrollEl = messagesScrollRef.current;
    if (!scrollEl) {
      return;
    }

    const messageCount = messages.length;
    const userJustSent = messageCount > prevMessageCountRef.current;
    prevMessageCountRef.current = messageCount;

    const distanceFromBottom =
      scrollEl.scrollHeight - scrollEl.scrollTop - scrollEl.clientHeight;
    const nearBottom = distanceFromBottom <= CHAT_SCROLL_STICKY_THRESHOLD_PX;

    if (userJustSent || nearBottom) {
      scrollEl.scrollTop = scrollEl.scrollHeight;
    }
  }, [messages, chatLoading]);

  const sendMessage = useCallback(
    async (query: string) => {
      const trimmed = query.trim();
      if (!trimmed || chatLoading) {
        return;
      }

      setChatError(null);
      setChatLoading(true);
      setDraft("");

      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: trimmed,
      };
      const assistantId = `assistant-${Date.now()}`;
      setMessages((current) => [
        ...current,
        userMessage,
        { id: assistantId, role: "assistant", content: "" },
      ]);

      try {
        const response = await fetch("/api/agent/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: trimmed,
            conversationId,
            inputs: agentInputs,
          }),
        });

        if (!response.ok) {
          const payload = (await response.json()) as { error?: string };
          throw new Error(payload.error || "Chat request failed.");
        }

        const streamResult = await readSseStream(response, (chunk) => {
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantId
                ? { ...message, content: message.content + chunk }
                : message,
            ),
          );
        });

        if (streamResult.conversationId) {
          setConversationId(streamResult.conversationId);
        }
      } catch (error) {
        setChatError(
          error instanceof Error ? error.message : "Chat request failed.",
        );
        setMessages((current) => current.filter((message) => message.id !== assistantId));
      } finally {
        setChatLoading(false);
      }
    },
    [agentInputs, chatLoading, conversationId],
  );

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void sendMessage(draft);
  };

  if (status && !status.enabled) {
    const missing = status.missing?.length
      ? status.missing.join("、")
      : "TW_AGENT_ENABLED、DIFY_API_URL、DIFY_STOCK_AGENT_API_KEY";

    return (
      <section className={PANEL_SECTION_CLASS}>
        <p className="text-xs uppercase tracking-[0.18em] text-on-surface-variant">
          AI Research
        </p>
        <h2 className="mt-1 text-xl font-bold text-on-surface">研究助手</h2>
        <p className="mt-3 text-sm leading-7 text-on-surface-variant">
          研究助手尚未启用。请在 <code className="text-on-surface">web/.env.local</code>{" "}
          中配置（修改后需重启 <code className="text-on-surface">npm run start</code>
          ）：
        </p>
        <ul className="mt-2 list-inside list-disc text-sm text-on-surface-variant">
          {(status.missing?.length
            ? status.missing
            : ["TW_AGENT_ENABLED=true", "DIFY_API_URL", "DIFY_STOCK_AGENT_API_KEY"]
          ).map((item) => (
            <li key={item}>
              <code className="text-on-surface">{item}</code>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-on-surface-variant">
          注意：Next.js 不会读取项目根目录的 <code className="text-on-surface">.env</code>
          ，Dify 相关变量必须写在 <code className="text-on-surface">web/.env.local</code>。
        </p>
      </section>
    );
  }

  return (
    <section className={PANEL_SECTION_CLASS}>
      <div className="mb-4 flex shrink-0 items-end justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-on-surface-variant">
            AI Research
          </p>
          <h2 className="text-xl font-bold text-on-surface">研究助手</h2>
        </div>
        <button
          type="button"
          className="rounded-sm border border-outline-variant/50 px-3 py-1.5 text-xs text-on-surface-variant transition hover:border-outline hover:text-on-surface disabled:opacity-50"
          onClick={() => void loadSummary()}
          disabled={summaryLoading || chatLoading}
        >
          刷新摘要
        </button>
      </div>

      <p className="mb-4 shrink-0 text-xs leading-relaxed text-on-surface-variant">
        AI 生成内容仅供研究参考，不构成投资建议。分析数字以 Twelvewin
        日终数据为准。
      </p>

      <div className="flex min-h-0 flex-[5] flex-col overflow-hidden rounded-sm border border-outline-variant/40 bg-surface-container-low p-4 lg:min-h-[13rem]">
        <h3 className="mb-2 shrink-0 text-sm font-semibold text-on-surface">研究摘要</h3>
        <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
          {summaryLoading ? (
            <p className="text-sm text-on-surface-variant">正在生成摘要…</p>
          ) : summaryError ? (
            <p className="text-sm text-error">{summaryError}</p>
          ) : summary ? (
            <AgentMessageBody content={summary} />
          ) : (
            <p className="text-sm text-on-surface-variant">暂无摘要。</p>
          )}
        </div>
      </div>

      <div className="mt-4 flex min-h-0 flex-[3] flex-col lg:mt-5">
        <h3 className="mb-3 shrink-0 text-sm font-semibold text-on-surface">继续提问</h3>
        <div className="mb-3 flex shrink-0 flex-wrap gap-2">
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="rounded-sm border border-outline-variant/40 px-3 py-1.5 text-xs text-on-surface-variant transition hover:border-outline hover:text-on-surface disabled:opacity-50"
              onClick={() => void sendMessage(prompt)}
              disabled={chatLoading}
            >
              {prompt}
            </button>
          ))}
        </div>

        <div
          ref={messagesScrollRef}
          className="min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain rounded-sm border border-outline-variant/40 bg-surface-container-low p-4 lg:max-h-[min(16rem,32vh)]"
        >
          {messages.length === 0 ? (
            <p className="text-sm text-on-surface-variant">
              输入问题，助手会通过 Twelvewin 研究 API 查询数据后回答。
            </p>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={
                  message.role === "user"
                    ? "ml-8 rounded-sm bg-surface-container-high px-3 py-2 text-sm text-on-surface"
                    : "mr-4 rounded-sm border border-outline-variant/30 px-3 py-2 text-sm leading-7 text-on-surface"
                }
              >
                <p className="mb-1 text-[11px] font-medium text-on-surface-variant">
                  {message.role === "user" ? "你" : "助手"}
                </p>
                {message.role === "assistant" ? (
                  <AgentMessageBody content={message.content} />
                ) : (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                )}
              </div>
            ))
          )}
        </div>

        {chatError ? (
          <p className="mt-2 shrink-0 text-sm text-error">{chatError}</p>
        ) : null}

        <form className="mt-4 flex shrink-0 gap-2" onSubmit={onSubmit}>
          <input
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="例如：和银行业 peers 比估值如何？"
            className="min-w-0 flex-1 rounded-sm border border-outline-variant/50 bg-surface px-3 py-2 text-sm text-on-surface outline-none transition focus:border-outline"
            disabled={chatLoading}
          />
          <button
            type="submit"
            className="btn-primary-container shrink-0 rounded-sm px-4 py-2 text-sm font-semibold transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
            disabled={chatLoading || !draft.trim()}
          >
            {chatLoading ? "发送中…" : "发送"}
          </button>
        </form>
      </div>
    </section>
  );
}
