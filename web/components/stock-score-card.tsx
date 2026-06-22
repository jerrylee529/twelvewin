"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { RefreshCw } from "lucide-react";

import { useStockQuote } from "@/components/stock-quote-provider";
import { StockScoreSkeleton } from "@/components/stock-skeletons";
import { StockScoreRadar } from "@/components/stock-score-radar";
import {
  scoreToneClass,
  type AgentScoreResponse,
  type StockScorePayload,
} from "@/lib/agent-score";

type AgentStatus = {
  enabled: boolean;
  scoreEnabled?: boolean;
};

function cacheKey(code: string, dataAsOf: string | null | undefined): string {
  return `twelvewin:stock-score:${code}:${dataAsOf || "unknown"}`;
}

function readCachedScore(
  code: string,
  dataAsOf: string | null | undefined,
): AgentScoreResponse | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    const raw = sessionStorage.getItem(cacheKey(code, dataAsOf));
    if (!raw) {
      return null;
    }
    return JSON.parse(raw) as AgentScoreResponse;
  } catch {
    return null;
  }
}

function writeCachedScore(
  code: string,
  dataAsOf: string | null | undefined,
  payload: AgentScoreResponse,
): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    sessionStorage.setItem(cacheKey(code, dataAsOf), JSON.stringify(payload));
  } catch {
    // Ignore quota errors.
  }
}

function ScoreAnalysisPanel({ score }: { score: StockScorePayload }) {
  const hasStrengths = score.strengths.length > 0;
  const hasWeaknesses = score.weaknesses.length > 0;

  if (!hasStrengths && !hasWeaknesses && !score.summary) {
    return (
      <p className="text-sm text-on-surface-variant">暂无分析结论。</p>
    );
  }

  return (
    <div className="flex h-full flex-col gap-6">
      {score.summary ? (
        <div>
          <h3 className="text-sm font-semibold text-on-surface">综合结论</h3>
          <p className="mt-2 text-sm leading-7 text-on-surface">{score.summary}</p>
        </div>
      ) : null}

      {hasStrengths ? (
        <div>
          <h3 className="text-sm font-semibold text-bullish">优势</h3>
          <ul className="mt-2 space-y-2 text-sm leading-7 text-on-surface">
            {score.strengths.map((item) => (
              <li key={item} className="flex gap-2">
                <span className="mt-2 size-1.5 shrink-0 rounded-full bg-bullish" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {hasWeaknesses ? (
        <div>
          <h3 className="text-sm font-semibold text-bearish">短板</h3>
          <ul className="mt-2 space-y-2 text-sm leading-7 text-on-surface">
            {score.weaknesses.map((item) => (
              <li key={item} className="flex gap-2">
                <span className="mt-2 size-1.5 shrink-0 rounded-full bg-bearish" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

export function StockScoreCard({
  code,
  dataAsOf,
}: {
  code: string;
  dataAsOf?: string | null;
}) {
  const { data: quoteData } = useStockQuote();
  const stockName = quoteData?.quot?.name || code;

  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AgentScoreResponse | null>(null);

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

    void fetch("/api/agent")
      .then((response) => response.json())
      .then((payload: AgentStatus) => {
        if (!cancelled) {
          setStatus(payload);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setStatus({ enabled: false, scoreEnabled: false });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const loadScore = useCallback(
    async (force = false) => {
      if (!status?.scoreEnabled) {
        return;
      }

      if (!force) {
        const cached = readCachedScore(code, dataAsOf);
        if (cached) {
          setResult(cached);
          return;
        }
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/agent/score", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            inputs: agentInputs,
            data_as_of: dataAsOf || undefined,
            force,
          }),
        });

        const payload = (await response.json()) as AgentScoreResponse & {
          error?: string;
        };

        if (!response.ok) {
          throw new Error(payload.error || "Failed to load investment score.");
        }

        setResult(payload);
        writeCachedScore(code, dataAsOf, payload);
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Failed to load investment score.",
        );
      } finally {
        setLoading(false);
      }
    },
    [agentInputs, code, dataAsOf, status?.scoreEnabled],
  );

  useEffect(() => {
    if (!status?.scoreEnabled) {
      return;
    }
    void loadScore();
  }, [loadScore, status?.scoreEnabled]);

  if (status !== null && !status.scoreEnabled) {
    return null;
  }

  const score = result?.score;
  const totalScore = score?.total_score ?? null;
  const checkingStatus = status === null;
  const computingScore = loading && !score;

  return (
    <section className="scroll-mt-16 border-t border-outline-variant/40 pt-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-on-surface">AI投资价值评分</h2>
          <p className="mt-2 text-sm text-on-surface-variant">
            {checkingStatus
              ? "正在检查 AI 评分服务…"
              : `基于已发布 EOD 量化数据的 AI 综合研究指标${
                  score?.data_as_of || dataAsOf
                    ? ` · 数据截至 ${score?.data_as_of || dataAsOf}`
                    : ""
                }`}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void loadScore(true)}
          disabled={checkingStatus || computingScore}
          className="inline-flex items-center gap-1.5 rounded-sm border border-outline-variant/50 px-3 py-1.5 text-xs font-semibold text-on-surface transition hover:bg-surface-container-high disabled:cursor-not-allowed disabled:opacity-50"
        >
          <RefreshCw
            className={`size-3.5 ${loading ? "animate-spin" : ""}`}
          />
          刷新评分
        </button>
      </div>

      <div className="mt-6 rounded-lg border border-outline-variant/40 bg-surface-container-low p-5">
        {checkingStatus || computingScore ? <StockScoreSkeleton /> : null}

        {error ? (
          <p className="text-sm text-bearish">{error}</p>
        ) : null}

        {score && totalScore != null ? (
          <div className="space-y-6">
            <div className="flex items-end gap-4 border-b border-outline-variant/30 pb-5">
              <div
                className={`text-5xl font-bold tabular-nums leading-none ${scoreToneClass(totalScore)}`}
              >
                {totalScore}
              </div>
              <div>
                <p className="text-sm text-on-surface-variant">/ 100</p>
                <p className="mt-1 text-lg font-semibold text-on-surface">
                  {score.grade} · {score.grade_label}
                </p>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2 lg:items-stretch">
              <div className="flex min-h-[420px] items-center justify-center rounded-md border border-outline-variant/30 bg-surface/40 px-2 py-6 sm:px-4">
                <StockScoreRadar
                  className="w-full max-w-[520px]"
                  dimensions={score.dimensions}
                  seriesName={score.stock_name}
                />
              </div>

              <div className="rounded-md border border-outline-variant/30 bg-surface/40 p-4">
                <h3 className="text-sm font-semibold text-on-surface">分析结论</h3>
                <div className="mt-4">
                  <ScoreAnalysisPanel score={score} />
                </div>
              </div>
            </div>

            {score.risk_adjustment.deduction > 0 ? (
              <div className="rounded-md border border-outline-variant/40 bg-surface px-3 py-2 text-sm text-on-surface-variant">
                风险修正 −{score.risk_adjustment.deduction} 分
                {score.risk_adjustment.reasons.length > 0
                  ? `：${score.risk_adjustment.reasons.join("；")}`
                  : null}
              </div>
            ) : null}

            {score.data_gaps.length > 0 ? (
              <p className="text-xs text-on-surface-variant">
                数据缺口：{score.data_gaps.join("、")}
              </p>
            ) : null}
          </div>
        ) : null}

        {!loading && !error && result && !score ? (
          <p className="text-sm text-on-surface-variant">
            未能解析结构化评分，请刷新重试或检查 Dify Agent 输出格式。
            {result.markdown ? (
              <span className="mt-2 block whitespace-pre-wrap">{result.markdown}</span>
            ) : null}
          </p>
        ) : null}

        <p className="mt-6 border-t border-outline-variant/30 pt-4 text-xs leading-5 text-on-surface-variant">
          {score?.disclaimer ||
            "本评分基于 Twelvewin 已发布 EOD 数据，仅供研究参考，不构成投资建议。"}
        </p>
      </div>
    </section>
  );
}
