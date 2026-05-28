import type { RankingKey } from "@/lib/types";

export const technicalNavItems = [
  { href: "/technical/filter", key: "filter", label: "涨跌幅分析" },
  { href: "/technical/highest", key: "highest", label: "创历史新高" },
  { href: "/technical/lowest", key: "lowest", label: "创历史新低" },
  { href: "/technical/ma_long", key: "ma_long", label: "均线多头" },
  { href: "/technical/break_ma", key: "break_ma", label: "突破均线" },
  { href: "/technical/above_ma", key: "above_ma", label: "年线之上" },
] as const;

export const clusterNavItems = [
  { href: "/clusters/sz50", key: "sz50", label: "上证50" },
  { href: "/clusters/hs300", key: "hs300", label: "沪深300" },
  { href: "/clusters/zz500", key: "zz500", label: "中证500" },
  { href: "/clusters/all", key: "all", label: "全部股票" },
] as const;

export const CLUSTER_SECTION_TITLES: Record<string, string> = {
  sz50: "上证50",
  hs300: "沪深300",
  zz500: "中证500",
  all: "全部股票",
};

const CLUSTER_INDEX_KEYS = new Set(["sz50", "hs300", "zz500", "all"]);

export function getClusterTitle(section: string) {
  return CLUSTER_SECTION_TITLES[section] || decodeURIComponent(section);
}

export function isClusterNavChildActive(
  pathname: string,
  href: string,
  key: string,
) {
  if (pathname === href) {
    return true;
  }
  if (key !== "all") {
    return false;
  }
  const match = pathname.match(/^\/clusters\/([^/?]+)/);
  if (!match) {
    return false;
  }
  const section = decodeURIComponent(match[1]);
  return !CLUSTER_INDEX_KEYS.has(section);
}

export function isTechnicalNavChildActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function isNavChildActive(
  pathname: string,
  child: { href: string; key: string },
) {
  if (clusterNavItems.some((item) => item.key === child.key)) {
    return isClusterNavChildActive(pathname, child.href, child.key);
  }
  return isTechnicalNavChildActive(pathname, child.href);
}

export const primaryNavTabs = [
  { href: "/fundamentals?metric=pe", label: "基本面分析", match: /^\/fundamentals|^\/rankings/ },
  {
    href: "/technical/filter",
    label: "技术面分析",
    match: /^\/technical/,
    children: technicalNavItems,
  },
  {
    href: "/clusters/sz50",
    label: "板块分析",
    match: /^\/clusters/,
    children: clusterNavItems,
  },
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
    children: clusterNavItems,
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
