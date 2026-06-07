import type { Metadata } from "next";
import {
  RANKING_META,
  TECHNICAL_META,
  type RankingKey,
  type TechnicalKey,
} from "@/lib/types";
import { getClusterTitle } from "@/lib/navigation";

export const SITE_NAME = "团赢数据";

export function getSiteUrl(): string {
  const raw =
    process.env.NEXT_PUBLIC_SITE_URL ||
    process.env.SITE_URL ||
    "https://twelvewin.com";
  return raw.replace(/\/$/, "");
}

export function absoluteUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${getSiteUrl()}${normalized}`;
}

export const FUNDAMENTAL_METRIC_KEYS = Object.keys(RANKING_META) as RankingKey[];

export const TECHNICAL_KEYS = Object.keys(TECHNICAL_META) as TechnicalKey[];

export const CLUSTER_INDEX_SECTIONS = ["sz50", "hs300", "zz500"] as const;

export const PRICE_CHANGE_PERIOD_SLUGS = {
  week: "近一周",
  month: "近一月",
  quarter: "近三月",
  "half-year": "近半年",
  year: "近一年",
} as const;

export type PriceChangePeriodSlug = keyof typeof PRICE_CHANGE_PERIOD_SLUGS;

export const PRICE_CHANGE_SLUGS = Object.keys(
  PRICE_CHANGE_PERIOD_SLUGS,
) as PriceChangePeriodSlug[];

export function priceChangePath(slug: PriceChangePeriodSlug): string {
  return `/technical/filter/${slug}`;
}

export const VALUE_RANKING_META = {
  title: "内在价值排行",
  description: "按内在价值与收盘价偏离度筛选 A 股低估标的",
};

type InstrumentRow = {
  code: string;
  name: string;
  industry?: string | null;
};

type InstrumentsListResponse = {
  total: number;
  instruments: InstrumentRow[];
};

async function fetchJson<T>(path: string): Promise<T | null> {
  const base = (process.env.API_URL || "http://127.0.0.1:8090").replace(
    /\/$/,
    "",
  );
  try {
    const response = await fetch(`${base}${path}`, {
      headers: { Accept: "application/json" },
      next: { revalidate: 3600 },
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function fetchAllInstruments(): Promise<InstrumentRow[]> {
  const payload = await fetchJson<InstrumentsListResponse>("/api/v1/stocks/list");
  return payload?.instruments ?? [];
}

export async function fetchIndustryNames(): Promise<string[]> {
  const payload = await fetchJson<{ industries: Array<{ name: string }> }>(
    "/api/v1/industries",
  );
  return (payload?.industries ?? []).map((item) => item.name).filter(Boolean);
}

export function buildPageMetadata({
  title,
  description,
  path,
  keywords,
}: {
  title: string;
  description: string;
  path: string;
  keywords?: string[];
}): Metadata {
  const url = absoluteUrl(path);
  return {
    title,
    description,
    keywords,
    alternates: { canonical: url },
    openGraph: {
      title: `${title} · ${SITE_NAME}`,
      description,
      url,
      siteName: SITE_NAME,
      locale: "zh_CN",
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} · ${SITE_NAME}`,
      description,
    },
  };
}

export function buildStockMetadata({
  code,
  name,
  description,
}: {
  code: string;
  name: string;
  description: string;
}): Metadata {
  const title = `${name}(${code}) 估值、财务与技术信号`;
  return buildPageMetadata({
    title,
    description,
    path: `/stock/${code}`,
    keywords: [name, code, "A股", "估值", "财务指标", "技术分析"],
  });
}

export function buildStockDescription({
  code,
  name,
  trade,
  pe,
  week52Low,
  week52High,
  industry,
}: {
  code: string;
  name: string;
  trade?: number;
  pe?: number;
  week52Low?: number;
  week52High?: number;
  industry?: string | null;
}): string {
  const parts = [
    `${name}（${code}）`,
    industry ? `所属行业：${industry}` : null,
    trade && trade > 0 ? `最新价 ¥${trade.toFixed(2)}` : null,
    pe && pe > 0 ? `市盈率 ${pe.toFixed(2)}` : null,
    week52Low && week52High
      ? `52 周区间 ¥${week52Low.toFixed(2)} – ¥${week52High.toFixed(2)}`
      : null,
    "查看日终量化基本面、技术面筛选与行业聚类分析。",
  ].filter(Boolean);
  return parts.join("，");
}

export function buildFundamentalMetadata(metric: RankingKey): Metadata {
  const meta = RANKING_META[metric];
  return buildPageMetadata({
    title: `A股${meta.title}`,
    description: `${meta.description}。每日日终更新，支持筛选与导出。`,
    path: `/fundamentals?metric=${metric}`,
    keywords: ["A股", meta.title, "股票排行", "量化筛选"],
  });
}

export function buildTechnicalMetadata(key: TechnicalKey): Metadata {
  const meta = TECHNICAL_META[key];
  return buildPageMetadata({
    title: `A股${meta.title}`,
    description: `${meta.description}。基于日终行情计算，每日更新。`,
    path: `/technical/${key}`,
    keywords: ["A股", meta.title, "技术分析", "股票筛选"],
  });
}

export function buildPriceChangeMetadata(slug: PriceChangePeriodSlug): Metadata {
  const period = PRICE_CHANGE_PERIOD_SLUGS[slug];
  return buildPageMetadata({
    title: `A股${period}涨跌幅筛选`,
    description: `按${period}涨跌幅区间筛选 A 股走势变化，支持自定义区间与日终数据更新。`,
    path: priceChangePath(slug),
    keywords: ["A股", "涨跌幅", period, "技术分析"],
  });
}

export function buildClusterMetadata(section: string): Metadata {
  const title = getClusterTitle(section);
  const description = CLUSTER_INDEX_SECTIONS.includes(
    section as (typeof CLUSTER_INDEX_SECTIONS)[number],
  )
    ? `${title}成分股高维聚类可视化与相关性分析`
    : `${title}行业成分股聚类分析与相关性热力图`;
  return buildPageMetadata({
    title: `${title}股票聚类分析`,
    description: `${description}。基于日终行情 Pearson 相关与 t-SNE 降维。`,
    path: `/clusters/${encodeURIComponent(section)}`,
    keywords: ["A股", title, "板块聚类", "相关性分析"],
  });
}

export async function buildSitemapEntries(): Promise<
  Array<{
    url: string;
    lastModified?: Date;
    changeFrequency?:
      | "always"
      | "hourly"
      | "daily"
      | "weekly"
      | "monthly"
      | "yearly"
      | "never";
    priority?: number;
  }>
> {
  const siteUrl = getSiteUrl();
  const now = new Date();
  const entries: Array<{
    url: string;
    lastModified?: Date;
    changeFrequency?:
      | "always"
      | "hourly"
      | "daily"
      | "weekly"
      | "monthly"
      | "yearly"
      | "never";
    priority?: number;
  }> = [
    { url: `${siteUrl}/`, lastModified: now, changeFrequency: "weekly", priority: 1 },
    {
      url: `${siteUrl}/business`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 0.8,
    },
    {
      url: `${siteUrl}/clusters/all`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.7,
    },
    {
      url: `${siteUrl}/value`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 0.8,
    },
  ];

  for (const metric of FUNDAMENTAL_METRIC_KEYS) {
    entries.push({
      url: `${siteUrl}/fundamentals?metric=${metric}`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 0.8,
    });
  }

  for (const key of TECHNICAL_KEYS) {
    entries.push({
      url: `${siteUrl}/technical/${key}`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 0.8,
    });
  }

  for (const slug of PRICE_CHANGE_SLUGS) {
    entries.push({
      url: `${siteUrl}${priceChangePath(slug)}`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 0.7,
    });
  }

  for (const section of CLUSTER_INDEX_SECTIONS) {
    entries.push({
      url: `${siteUrl}/clusters/${section}`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.7,
    });
  }

  const [instruments, industries] = await Promise.all([
    fetchAllInstruments(),
    fetchIndustryNames(),
  ]);

  for (const instrument of instruments) {
    entries.push({
      url: `${siteUrl}/stock/${instrument.code}`,
      lastModified: now,
      changeFrequency: "daily",
      priority: 0.6,
    });
  }

  for (const industry of industries) {
    entries.push({
      url: `${siteUrl}/clusters/${encodeURIComponent(industry)}`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.6,
    });
  }

  return entries;
}
