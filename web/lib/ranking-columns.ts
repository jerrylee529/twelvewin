import type { ColumnDef, Row } from "@tanstack/react-table";
import type { ReactNode } from "react";
import type { RankingKey } from "@/lib/types";
import { formatCompactNumber } from "@/lib/stock-format";

export type RankingRow = Record<string, unknown>;

/** Columns published in 万元 that should render as 万/亿/万亿. */
export const MARKET_CAP_KEYS = new Set([
  "market_cap",
  "float_market_cap",
  "mktcap",
  "nmc",
]);

/** Signed percentage columns: red when positive, green when negative. */
export const SIGNED_PERCENT_KEYS = new Set([
  "rate",
  "revenue_growth",
  "profit_growth",
  "rev",
  "profit",
]);

export function formatMarketCapCell(value: unknown): string {
  const numeric = parseRankingNumber(value);
  if (numeric == null || numeric === 0) {
    return "—";
  }
  return formatCompactNumber(numeric * 10000);
}

/** A-share convention: red for gains, green for losses. */
export function signedToneClass(value: unknown): string {
  const numeric = parseRankingNumber(value);
  if (numeric == null || numeric === 0) {
    return "text-on-surface-variant";
  }
  return numeric > 0 ? "text-bullish" : "text-bearish";
}

export function formatSignedPercent(value: unknown): string {
  const numeric = parseRankingNumber(value);
  if (numeric == null) {
    return formatRankingValue(value);
  }
  const prefix = numeric > 0 ? "+" : "";
  return `${prefix}${formatRankingValue(value)}%`;
}

export function compareRankingValues(a: unknown, b: unknown): number {
  const numericA = parseRankingNumber(a);
  const numericB = parseRankingNumber(b);
  if (numericA != null && numericB != null) {
    return numericA - numericB;
  }
  if (numericA != null) {
    return 1;
  }
  if (numericB != null) {
    return -1;
  }
  return String(a ?? "").localeCompare(String(b ?? ""), "zh-CN");
}

export function rankingSortingFn(
  rowA: Row<RankingRow>,
  rowB: Row<RankingRow>,
  columnId: string,
): number {
  return compareRankingValues(rowA.original[columnId], rowB.original[columnId]);
}

export const RANKING_COLUMN_ORDER = [
  "id",
  "code",
  "name",
  "industry",
  "is_st",
  "year",
  "report_date",
  "divi",
  "shares",
  "pe_ttm",
  "per",
  "pe",
  "pb_lf",
  "pb",
  "outstanding",
  "totals",
  "totalAssets",
  "reservedPerShare",
  "esp",
  "bvps",
  "roe",
  "roe_y1",
  "roe_y2",
  "roe_y3",
  "rev",
  "profit",
  "gpr",
  "close",
  "dividend_yield",
  "rate",
  "valueprice",
  "market_cap",
  "float_market_cap",
  "mktcap",
  "nmc",
  "turnoverratio",
  "pe_discount_to_industry",
  "pb_discount_to_industry",
  "revenue_growth",
  "profit_growth",
  "updateTime",
] as const;

export const RANKING_COLUMN_LABELS: Record<string, string> = {
  id: "序号",
  code: "代码",
  name: "名称",
  industry: "行业",
  is_st: "ST",
  year: "年份",
  report_date: "发布日期",
  divi: "分红金额",
  shares: "送股或转增(每10股)",
  pe_ttm: "市盈率(TTM)",
  per: "市盈率(PE)",
  pb_lf: "市净率(LF)",
  pb: "市净率(PB)",
  roe: "净资产收益率(ROE)",
  roe_y1: "ROE 年度1",
  roe_y2: "ROE 年度2",
  roe_y3: "ROE 年度3",
  close: "股价",
  dividend_yield: "股息率(%)",
  rate: "涨跌幅(%)",
  valueprice: "估值",
  market_cap: "总市值",
  float_market_cap: "流通市值",
  mktcap: "总市值",
  nmc: "流通市值",
  turnoverratio: "换手率(%)",
  pe_discount_to_industry: "PE 行业折价",
  pb_discount_to_industry: "PB 行业折价",
  revenue_growth: "营收增长率(%)",
  profit_growth: "利润增长率(%)",
  pe: "市盈率",
  outstanding: "流通股本(亿)",
  totals: "总股本(亿)",
  totalAssets: "总资产(万)",
  reservedPerShare: "每股公积金",
  esp: "每股收益",
  bvps: "每股净资产",
  rev: "收入同比(%)",
  profit: "利润同比(%)",
  gpr: "毛利率(%)",
  updateTime: "更新时间",
};

const METRIC_SORT_FIELD: Record<RankingKey, string> = {
  pe: "pe_ttm",
  pb: "pb_lf",
  roe: "roe",
  divi: "dividend_yield",
};

export function getMetricSortField(metric: RankingKey) {
  return METRIC_SORT_FIELD[metric];
}

export function parseRankingNumber(value: unknown) {
  const parsed = parseFloat(String(value));
  return Number.isFinite(parsed) ? parsed : null;
}

export function formatRankingValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const text = String(value).trim();
  if (!text || text === "NaT" || text === "nan" || text === "None") {
    return "—";
  }

  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(2);
  }

  if (/^\d{4}-\d{2}-\d{2}/.test(text)) {
    return text.slice(0, 10);
  }

  const numeric = parseRankingNumber(text);
  if (numeric != null && /^-?\d+(\.\d+)?$/.test(text)) {
    return Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(2);
  }

  return text;
}

export function formatStockCodeValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const text = String(value).trim();
  if (!text || text === "NaT" || text === "nan" || text === "None") {
    return "—";
  }

  const integerText =
    typeof value === "number" && Number.isFinite(value)
      ? String(Math.trunc(value))
      : text.replace(/\.0+$/, "");

  if (/^\d+$/.test(integerText) && integerText.length < 6) {
    return integerText.padStart(6, "0");
  }

  return text;
}

export function isUndervalued(row: RankingRow) {
  const close = parseRankingNumber(row.close);
  const valueprice = parseRankingNumber(row.valueprice);
  return close != null && valueprice != null && valueprice > close;
}

export function resolveRankingColumns(
  rows: RankingRow[],
  options?: { includeUpdateTime?: boolean },
) {
  const includeUpdateTime = options?.includeUpdateTime ?? false;

  if (rows.length === 0) {
    return [...RANKING_COLUMN_ORDER].filter(
      (key) => includeUpdateTime || key !== "updateTime",
    );
  }

  const rowKeys = new Set(Object.keys(rows[0]));
  return RANKING_COLUMN_ORDER.filter(
    (key) =>
      rowKeys.has(key) && (includeUpdateTime || key !== "updateTime"),
  );
}

export function buildRankingColumnDefs(
  rows: RankingRow[],
  renderers: {
    code: (value: unknown) => ReactNode;
    name: (row: RankingRow, value: unknown) => ReactNode;
    default: (key: string, row: RankingRow, value: unknown) => ReactNode;
  },
  options?: { includeUpdateTime?: boolean },
): ColumnDef<RankingRow>[] {
  const keys = resolveRankingColumns(rows, options);

  return keys.map((key) => ({
    accessorKey: key,
    header: RANKING_COLUMN_LABELS[key] || key,
    sortingFn: rankingSortingFn,
    cell: ({ row }) => {
      const value = row.original[key];

      if (key === "code") {
        return renderers.code(value);
      }

      if (key === "name") {
        return renderers.name(row.original, value);
      }

      return renderers.default(key, row.original, value);
    },
  }));
}

export function exportRankingCsv(
  rows: RankingRow[],
  filename = "fundamentals.csv",
) {
  if (rows.length === 0) {
    return;
  }

  const keys = resolveRankingColumns(rows);
  const header = keys.map((key) => RANKING_COLUMN_LABELS[key] || key).join(",");
  const body = rows
    .map((row) =>
      keys
        .map((key) => {
          const cell =
            key === "code"
              ? formatStockCodeValue(row[key])
              : formatRankingValue(row[key]);
          return cell.includes(",") ? `"${cell}"` : cell;
        })
        .join(","),
    )
    .join("\n");

  const blob = new Blob([`\ufeff${header}\n${body}`], {
    type: "text/csv;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
