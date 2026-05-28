import type {
  BarsResponse,
  ClusterChartPayload,
  ClusterResponse,
  DataStatusResponse,
  FundamentalScreenerQuery,
  InstrumentsResponse,
  IndustriesResponse,
  PriceChangePeriod,
  ProfileResponse,
  QuoteResponse,
  RankingKey,
  TableResponse,
  TechnicalKey,
} from "@/lib/types";

/** Max trading days fetched for the stock chart (covers 5Y range). */
export const STOCK_BARS_MAX_DAYS = 1260;

type FetchJsonOptions = {
  revalidate?: number | false;
  cache?: RequestCache;
};

function getApiBase(): string {
  if (typeof window === "undefined") {
    return (process.env.API_URL || "http://127.0.0.1:8090").replace(/\/$/, "");
  }
  return (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
}

async function fetchJson<T>(
  path: string,
  init?: RequestInit,
  options?: FetchJsonOptions,
): Promise<T> {
  const base = getApiBase();
  const url = base ? `${base}${path}` : path;
  const revalidate = options?.revalidate;

  const response = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.headers || {}),
    },
    cache:
      options?.cache ??
      (revalidate === false ? "no-store" : undefined),
    next:
      revalidate === false
        ? undefined
        : { revalidate: revalidate ?? 60 },
  });

  if (!response.ok) {
    throw new Error(`API ${response.status}: ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function fetchStockQuoteClient(
  code: string,
): Promise<QuoteResponse> {
  const response = await fetch(
    `/api/v1/stocks/${encodeURIComponent(code)}/quote`,
    {
      headers: { Accept: "application/json" },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(`API ${response.status}: ${response.statusText}`);
  }

  return response.json() as Promise<QuoteResponse>;
}

export function getDataStatus() {
  return fetchJson<DataStatusResponse>("/api/v1/data-status");
}

export function getRanking(key: RankingKey, preview = false) {
  const query = preview ? "?preview=true" : "";
  return fetchJson<TableResponse>(`/api/v1/rankings/${key}${query}`);
}

export function getFundamentalScreener(query: FundamentalScreenerQuery = {}) {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      params.set(key, String(value));
    }
  });
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return fetchJson<TableResponse>(`/api/v1/fundamentals/screener${suffix}`);
}

export function getTechnical(key: TechnicalKey, preview = false) {
  const query = preview ? "?preview=true" : "";
  return fetchJson<TableResponse>(`/api/v1/technical/${key}${query}`);
}

export function getPriceChange(
  days: PriceChangePeriod = "近一周",
  low: string | number = -30,
  high: string | number = 0,
) {
  const params = new URLSearchParams({
    days,
    low: String(low),
    high: String(high),
  });

  return fetchJson<TableResponse>(
    `/api/v1/technical/filter/price-change?${params}`,
  );
}

export function getBusiness(labels = "") {
  const query = labels ? `?labels=${encodeURIComponent(labels)}` : "";
  return fetchJson<TableResponse>(`/api/v1/business${query}`);
}

export function searchInstruments(query: string, limit = 20) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return fetchJson<InstrumentsResponse>(`/api/v1/stocks/search?${params}`);
}

export function getStockBars(
  code: string,
  options: { days?: number; includeQuote?: boolean } = {},
) {
  const params = new URLSearchParams();
  const days = options.days ?? STOCK_BARS_MAX_DAYS;
  params.set("days", String(days));
  if (options.includeQuote) {
    params.set("include_quote", "true");
  }
  return fetchJson<BarsResponse>(
    `/api/v1/stocks/${encodeURIComponent(code)}/bars?${params}`,
    undefined,
    { revalidate: 300 },
  );
}

export function getStockQuote(code: string) {
  return fetchJson<QuoteResponse>(
    `/api/v1/stocks/${encodeURIComponent(code)}/quote`,
    undefined,
    { revalidate: false },
  );
}

export function getStockProfile(code: string) {
  return fetchJson<ProfileResponse>(
    `/api/v1/stocks/${encodeURIComponent(code)}/profile`,
    undefined,
    { revalidate: 3600 },
  );
}

export function getCluster(section: string) {
  return fetchJson<ClusterResponse>(
    `/api/v1/clusters/${encodeURIComponent(section)}`,
  );
}

export function getClusterChart(section: string) {
  return fetchJson<ClusterChartPayload>(
    `/api/v1/clusters/${encodeURIComponent(section)}/chart`,
  );
}

export function getIndustries() {
  return fetchJson<IndustriesResponse>("/api/v1/industries");
}
