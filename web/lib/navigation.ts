import type { RankingKey } from "@/lib/types";

export const technicalNavItems = [
  { href: "/technical/filter", key: "filter", label: "涨跌幅分析" },
  { href: "/technical/highest", key: "highest", label: "创历史新高" },
  { href: "/technical/lowest", key: "lowest", label: "创历史新低" },
  { href: "/technical/ma_long", key: "ma_long", label: "均线多头" },
  { href: "/technical/break_ma", key: "break_ma", label: "突破均线" },
  { href: "/technical/above_ma", key: "above_ma", label: "年线之上" },
] as const;

export const primaryNavTabs = [
  { href: "/fundamentals?metric=pe", label: "基本面分析", match: /^\/fundamentals|^\/rankings/ },
  {
    href: "/technical/filter",
    label: "技术面分析",
    match: /^\/technical/,
    children: technicalNavItems,
  },
  { href: "/clusters/sz50", label: "板块分析", match: /^\/clusters/ },
  { href: "/business", label: "行业分析", match: /^\/business/ },
] as const;

export const sidebarNavItems = [
  {
    href: "/fundamentals?metric=pe",
    label: "基本面",
    match: /^\/fundamentals|^\/rankings/,
  },
  {
    href: "/technical/filter",
    label: "技术图",
    match: /^\/technical/,
    children: technicalNavItems,
  },
  {
    href: "/clusters/sz50",
    label: "板块聚类",
    match: /^\/clusters/,
  },
  {
    href: "/business",
    label: "行业分析",
    match: /^\/business/,
  },
] as const;

export const fundamentalMetrics: Array<{
  key: RankingKey;
  label: string;
  shortLabel: string;
}> = [
  { key: "pe", label: "市盈率 (PE)", shortLabel: "市盈率" },
  { key: "pb", label: "市净率 (PB)", shortLabel: "市净率" },
  { key: "roe", label: "净资产收益率 (ROE)", shortLabel: "ROE" },
  { key: "divi", label: "股息率", shortLabel: "股息率" },
];

export function formatStockCode(code: string) {
  const normalized = String(code).trim();
  if (normalized.includes(".")) {
    return normalized;
  }
  if (normalized.startsWith("6")) {
    return `${normalized}.SH`;
  }
  if (normalized.startsWith("0") || normalized.startsWith("3")) {
    return `${normalized}.SZ`;
  }
  return normalized;
}
