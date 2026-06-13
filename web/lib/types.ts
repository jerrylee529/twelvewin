export type TableResponse = {
  total: number;
  rows: Record<string, unknown>[];
  updateTime?: string | null;
  error?: string | null;
};

export type InstrumentsResponse = {
  instruments: Array<{
    id: number;
    code: string;
    name: string;
    industry?: string | null;
  }>;
};

export type IndustriesResponse = {
  industries: Array<{
    id: number;
    name: string;
  }>;
};

export type BarsResponse = {
  rows: Array<[string, number, number, number, number, number?]>;
  updateTime?: string | null;
  error?: string | null;
};

export type ResearchContextResponse = {
  code?: string | null;
  name?: string | null;
  industry?: string | null;
  data_as_of?: string | null;
  labels?: string | null;
  fundamentals?: {
    pe_ttm?: number | null;
    pb_lf?: number | null;
    roe?: number | null;
    dividend_yield?: number | null;
    market_cap?: number | null;
    float_market_cap?: number | null;
    pe_discount_to_industry?: number | null;
    pb_discount_to_industry?: number | null;
    close?: number | null;
    updateTime?: string | null;
  } | null;
  industry_benchmark?: {
    industry?: string;
    median_pe_ttm?: number | null;
    median_pb_lf?: number | null;
    median_roe?: number | null;
    median_dividend_yield?: number | null;
    stock_count?: number | null;
    trade_date?: string | null;
  } | null;
  technical_signals?: string[];
  rankings?: Record<string, number>;
  quote?: Record<string, unknown> | null;
  bars_summary?: Record<string, unknown> | null;
  finance_profile?: Record<string, unknown>;
  cluster_peers?: Array<{
    code?: string;
    name?: string;
    pe?: number | null;
    pb?: number | null;
    label?: string | null;
  }>;
  artifacts_freshness?: Record<string, unknown>;
  errors?: Record<string, unknown>;
  error?: string | null;
};

export type QuoteResponse = {
  quot?: Record<string, string> | null;
  quot_source?: "redis" | "daily_bar" | null;
};

export type ProfileResponse = {
  quot?: Record<string, string> | null;
  quot_source?: "redis" | "daily_bar" | null;
  net_profit_after_nrgal_atsolc: Array<{ date: string; value: number }>;
  avg_roe: Array<{ date: string; value: number }>;
  np_atsopc_nrgal_yoy: Array<{ date: string; value: number }>;
  basic_eps: Array<{ date: string; value: number }>;
  gross_selling_rate: Array<{ date: string; value: number }>;
  np_per_share: Array<{ date: string; value: number }>;
};

export type DataStatusResponse = {
  artifacts: Record<
    string,
    Record<
      string,
      {
        result_key: string;
        category: string;
        exists: boolean;
        update_time: string | null;
        row_count: number;
        source_file?: string | null;
      }
    >
  >;
  jobs: Record<string, unknown>;
};

export type ClusterRow = {
  id: number;
  code: string;
  name: string;
  items: Array<{ code: string; name: string; corr: number }>;
};

export type ClusterResponse = {
  total: number;
  rows: ClusterRow[];
  updateTime?: string | null;
  error?: string | null;
};

export type ClusterChartNode = {
  code: string;
  name: string;
  clusterId: number;
  clusterName: string;
  x: number;
  y: number;
};

export type ClusterChartEdge = {
  source: string;
  target: string;
  corr: number;
};

export type ClusterChartPayload = {
  nodes: ClusterChartNode[];
  edges: ClusterChartEdge[];
  heatmap: {
    labels: Array<{ code: string; name: string; clusterId: number }>;
    values: number[][];
  };
  clusters: Array<{ id: number; code: string; name: string; size: number }>;
  meta: {
    edgeThreshold?: number;
    stockCount?: number;
    valueMode?: string;
  };
  updateTime?: string | null;
  error?: string | null;
};

export type RankingKey = "pe" | "pb" | "roe" | "divi";

export type FundamentalScreenerQuery = {
  metric?: RankingKey;
  search?: string;
  industry?: string;
  pe_min?: string;
  pe_max?: string;
  pb_min?: string;
  pb_max?: string;
  roe_min?: string;
  roe_3y_min?: string;
  dividend_yield_min?: string;
  float_market_cap_min?: string;
  float_market_cap_max?: string;
  exclude_st?: string;
  sort?: string;
  order?: "asc" | "desc";
  page?: string;
  page_size?: string;
};

export type TechnicalKey =
  | "highest"
  | "lowest"
  | "ma_long"
  | "break_ma"
  | "above_ma";

export type PriceChangePeriod =
  | "近一周"
  | "近一月"
  | "近三月"
  | "近半年"
  | "近一年";

export const RANKING_META: Record<
  RankingKey,
  { title: string; description: string }
> = {
  pe: { title: "市盈率排行", description: "按市盈率从低到高筛选 A 股" },
  pb: { title: "市净率排行", description: "按市净率从低到高筛选 A 股" },
  roe: { title: "净资产收益率排行", description: "按 ROE 从高到低筛选 A 股" },
  divi: { title: "现金股息率排行", description: "按股息率从高到低筛选 A 股" },
};

export const RANKING_DISPLAY_META: Record<
  string,
  { title: string; description: string }
> = {
  ...RANKING_META,
  value: { title: "价值分析排行", description: "综合价值因子筛选 A 股" },
};

export const TECHNICAL_META: Record<
  TechnicalKey,
  { title: string; description: string }
> = {
  highest: { title: "创历史新高", description: "股价创历史新高的个股" },
  lowest: { title: "创历史新低", description: "股价创历史新低的个股" },
  ma_long: { title: "均线多头", description: "5/10/20 日均线呈多头排列" },
  break_ma: { title: "突破均线", description: "突破 20 日均线的个股" },
  above_ma: { title: "年线之上", description: "位于 250 日均线之上的个股" },
};
