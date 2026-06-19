"use client";

import { useEffect, useMemo, useState } from "react";
import { FileText, LoaderCircle, RefreshCw } from "lucide-react";

import {
  filingHighlightsToStrings,
  filingRisksToStrings,
  type FilingAnalysisPayload,
  type FilingListRow,
} from "@/lib/agent-filing";

type AgentStatus = {
  enabled: boolean;
  filingEnabled?: boolean;
};

export function StockFilingSection({
  code,
  stockName,
}: {
  code: string;
  stockName: string;
}) {
  const [filings, setFilings] = useState<FilingListRow[]>([]);
  const [selectedKey, setSelectedKey] = useState<string>("");
  const [analysis, setAnalysis] = useState<FilingAnalysisPayload | null>(null);
  const [listLoading, setListLoading] = useState(true);
  const [analyzeLoading, setAnalyzeLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);

  const selectedFiling = useMemo(() => {
    if (!selectedKey) {
      return filings[0] ?? null;
    }
    return (
      filings.find((item) => `${item.year}-${item.season}` === selectedKey) ??
      filings[0] ??
      null
    );
  }, [filings, selectedKey]);

  useEffect(() => {
    void fetch("/api/agent", { cache: "no-store" })
      .then((response) => response.json())
      .then((payload) => setAgentStatus(payload as AgentStatus))
      .catch(() => setAgentStatus({ enabled: false }));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setListLoading(true);
    setError(null);

    void fetch(`/api/v1/stocks/${encodeURIComponent(code)}/filings`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`加载财报列表失败 (${response.status})`);
        }
        return response.json() as Promise<{ rows?: FilingListRow[] }>;
      })
      .then((payload) => {
        if (cancelled) {
          return;
        }
        const rows = payload.rows ?? [];
        setFilings(rows);
        if (rows[0]) {
          setSelectedKey(`${rows[0].year}-${rows[0].season}`);
        }
      })
      .catch((fetchError) => {
        if (!cancelled) {
          setError(
            fetchError instanceof Error
              ? fetchError.message
              : "加载财报列表失败",
          );
        }
      })
      .finally(() => {
        if (!cancelled) {
          setListLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [code]);

  const handleSelectFiling = (nextKey: string) => {
    setSelectedKey(nextKey);
    setAnalysis(null);
    setError(null);
  };

  const runAnalysis = async () => {
    if (!selectedFiling) {
      return;
    }
    if (!agentStatus?.filingEnabled) {
      setError("财报 AI 解读未配置，请设置 DIFY_FILING_ANALYSIS_API_KEY。");
      return;
    }

    setAnalyzeLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/agent/filing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          inputs: {
            stock_code: code,
            stock_name: stockName,
            year: selectedFiling.year,
            season: selectedFiling.season,
            locale: "zh-CN",
          },
        }),
      });

      const payload = (await response.json()) as {
        analysis?: FilingAnalysisPayload;
        error?: string;
        warning?: string;
      };

      if (!response.ok) {
        throw new Error(payload.error || "AI 解读请求失败");
      }

      const result = payload.analysis;
      if (!result) {
        throw new Error("AI 解读返回为空");
      }

      setAnalysis(result);
      if (payload.warning) {
        setError(payload.warning);
      }
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "AI 解读失败");
    } finally {
      setAnalyzeLoading(false);
    }
  };

  const highlights = filingHighlightsToStrings(analysis?.highlights);
  const risks = filingRisksToStrings(analysis?.risks);

  return (
    <section
      id="stock-filing"
      className="mt-8 rounded-2xl border border-outline-variant/50 bg-surface-container-lowest p-5 sm:p-6"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-on-surface">财报解读</h2>
          <p className="mt-1 text-sm text-on-surface-variant">
            基于七牛云 PDF 年报/季报的 AI 结构化解读
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {filings.length > 0 ? (
            <select
              value={
                selectedFiling
                  ? `${selectedFiling.year}-${selectedFiling.season}`
                  : ""
              }
              onChange={(event) => handleSelectFiling(event.target.value)}
              className="rounded-xl border border-outline-variant/60 bg-surface px-3 py-2 text-sm text-on-surface"
            >
              {filings.map((item) => (
                <option key={item.id} value={`${item.year}-${item.season}`}>
                  {item.display_label}
                  {item.publish_date ? ` · 披露 ${item.publish_date}` : ""}
                </option>
              ))}
            </select>
          ) : null}
          <button
            type="button"
            onClick={() => void runAnalysis()}
            disabled={!selectedFiling || analyzeLoading}
            className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-on-primary transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {analyzeLoading ? (
              <LoaderCircle className="size-4 animate-spin" />
            ) : (
              <RefreshCw className="size-4" />
            )}
            {analysis ? "重新解读" : "AI 解读"}
          </button>
        </div>
      </div>

      {listLoading ? (
        <p className="mt-6 text-sm text-on-surface-variant">正在加载财报列表…</p>
      ) : null}

      {!listLoading && filings.length === 0 ? (
        <div className="mt-6 flex items-start gap-3 rounded-xl border border-dashed border-outline-variant/70 bg-surface p-4 text-sm text-on-surface-variant">
          <FileText className="mt-0.5 size-4 shrink-0" />
          <div>
            <p>暂无已同步的 PDF 财报。</p>
            <p className="mt-1">
              请先配置七牛云并在服务端运行{" "}
              <code className="rounded bg-surface-container-high px-1.5 py-0.5 text-xs">
                python -m compute filing_pipeline
              </code>
              。
            </p>
          </div>
        </div>
      ) : null}

      {error ? (
        <p className="mt-4 rounded-xl border border-bearish/30 bg-bearish/5 px-4 py-3 text-sm text-bearish">
          {error}
        </p>
      ) : null}

      {selectedFiling ? (
        <div className="mt-4 flex flex-wrap gap-3 text-xs text-on-surface-variant">
          <span>文件：{selectedFiling.filename}</span>
          <span>状态：{selectedFiling.analysis_status}</span>
          {selectedFiling.page_count ? (
            <span>页数：{selectedFiling.page_count}</span>
          ) : null}
        </div>
      ) : null}

      {analyzeLoading ? (
        <p className="mt-6 text-sm text-on-surface-variant">正在生成 AI 解读…</p>
      ) : null}

      {!analyzeLoading && analysis ? (
        <div className="mt-6 space-y-6">
          {analysis.summary ? (
            <div>
              <h3 className="text-sm font-semibold text-on-surface">业绩概要</h3>
              <p className="mt-2 text-sm leading-7 text-on-surface">
                {analysis.summary}
              </p>
            </div>
          ) : null}

          {highlights.length > 0 ? (
            <div>
              <h3 className="text-sm font-semibold text-bullish">核心亮点</h3>
              <ul className="mt-2 space-y-2 text-sm leading-7 text-on-surface">
                {highlights.map((item) => (
                  <li key={item} className="flex gap-2">
                    <span className="mt-2 size-1.5 shrink-0 rounded-full bg-bullish" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {risks.length > 0 ? (
            <div>
              <h3 className="text-sm font-semibold text-bearish">风险提示</h3>
              <ul className="mt-2 space-y-2 text-sm leading-7 text-on-surface">
                {risks.map((item) => (
                  <li key={item} className="flex gap-2">
                    <span className="mt-2 size-1.5 shrink-0 rounded-full bg-bearish" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          {analysis.full_markdown ? (
            <div>
              <h3 className="text-sm font-semibold text-on-surface">详细解读</h3>
              <div className="mt-2 whitespace-pre-wrap text-sm leading-7 text-on-surface">
                {analysis.full_markdown}
              </div>
            </div>
          ) : null}

          <p className="text-xs text-on-surface-variant">
            {analysis.disclaimer ||
              "本解读由 AI 生成，不构成投资建议。请结合 PDF 原文与官方披露信息判断。"}
          </p>
        </div>
      ) : null}

      {!analyzeLoading && !analysis && filings.length > 0 ? (
        <p className="mt-6 text-sm text-on-surface-variant">
          请选择报告后点击「AI 解读」开始分析。
        </p>
      ) : null}
    </section>
  );
}
