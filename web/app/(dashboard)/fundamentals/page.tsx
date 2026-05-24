import { EmptyState } from "@/components/dashboard-shell";
import { FundamentalsWorkspace } from "@/components/fundamentals-workspace";
import { getFundamentalScreener } from "@/lib/api";
import {
  RANKING_META,
  type FundamentalScreenerQuery,
  type RankingKey,
  type TableResponse,
} from "@/lib/types";

const VALID_METRICS = new Set<string>(Object.keys(RANKING_META));

const PRESETS: Record<RankingKey, FundamentalScreenerQuery> = {
  pe: { metric: "pe", pe_min: "5", pe_max: "20", sort: "pe_ttm", order: "asc" },
  pb: { metric: "pb", pb_max: "2", sort: "pb_lf", order: "asc" },
  roe: { metric: "roe", roe_min: "10", sort: "roe", order: "desc" },
  divi: {
    metric: "divi",
    dividend_yield_min: "3",
    sort: "dividend_yield",
    order: "desc",
  },
};

const EMPTY_RESPONSE: TableResponse = {
  total: 0,
  rows: [],
  updateTime: null,
  error: "API unavailable",
};

export default async function FundamentalsPage({
  searchParams,
}: {
  searchParams: Promise<FundamentalScreenerQuery>;
}) {
  const params = await searchParams;
  const metricParam = params.metric;
  const metric = VALID_METRICS.has(metricParam ?? "") ? (metricParam as RankingKey) : "pe";
  const meta = RANKING_META[metric];
  const query: FundamentalScreenerQuery = {
    ...PRESETS[metric],
    ...params,
    metric,
    page_size: params.page_size ?? "50",
  };

  let data: TableResponse = EMPTY_RESPONSE;
  try {
    data = await getFundamentalScreener(query);
  } catch {
    data = EMPTY_RESPONSE;
  }

  if (data.error && data.rows.length === 0) {
    return (
      <>
        <div className="mb-6">
          <h1 className="text-lg font-semibold text-on-surface">{meta.title}</h1>
          <p className="mt-1 text-xs text-on-surface-variant">{meta.description}</p>
        </div>
        <EmptyState
          message={
            data.error === "API unavailable"
              ? "无法连接分析 API"
              : "暂无已发布的数据"
          }
          hint={
            data.error === "API unavailable"
              ? "请确认 uvicorn api.main:app --port 8090 已启动。"
              : "请先运行 python -m compute ranking_pipeline 生成基本面快照。"
          }
        />
      </>
    );
  }

  return (
    <FundamentalsWorkspace
      metric={metric}
      query={query}
      rows={data.rows}
      total={data.total}
      updateTime={data.updateTime}
    />
  );
}
