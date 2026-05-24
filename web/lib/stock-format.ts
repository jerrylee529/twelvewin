export type BarRow = [string, number, number, number, number];

export type ChartRange = "1D" | "1W" | "1M" | "3M" | "YTD" | "1Y" | "5Y" | "ALL";

export const CHART_RANGES: ChartRange[] = [
  "1D",
  "1W",
  "1M",
  "3M",
  "YTD",
  "1Y",
  "5Y",
  "ALL",
];

export function parseNumber(value: string | undefined | null): number {
  const parsed = parseFloat(value || "0");
  return Number.isFinite(parsed) ? parsed : 0;
}

export function formatPrice(value: number, digits = 2): string {
  return value.toLocaleString("zh-CN", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatPercent(value: number, digits = 2): string {
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(digits)}%`;
}

export function formatCompactNumber(value: number): string {
  if (!Number.isFinite(value) || value === 0) {
    return "—";
  }

  const abs = Math.abs(value);
  if (abs >= 1e12) {
    return `${(value / 1e12).toFixed(2)}万亿`;
  }
  if (abs >= 1e8) {
    return `${(value / 1e8).toFixed(2)}亿`;
  }
  if (abs >= 1e4) {
    return `${(value / 1e4).toFixed(2)}万`;
  }
  return formatPrice(value, 0);
}

/** Tushare mktcap is typically in 万元 (10k CNY). */
export function formatMarketCap(raw: string | undefined | null): string {
  const value = parseNumber(raw);
  if (value === 0) {
    return "—";
  }
  return formatCompactNumber(value * 10000);
}

export function formatVolume(raw: string | undefined | null): string {
  const value = parseNumber(raw);
  if (value === 0) {
    return "—";
  }
  return formatCompactNumber(value);
}

export function compute52WeekRange(rows: BarRow[]): {
  high: number;
  low: number;
} {
  const lookback = rows.slice(-252);
  if (lookback.length === 0) {
    return { high: 0, low: 0 };
  }

  let high = -Infinity;
  let low = Infinity;
  for (const [, , , rowLow, rowHigh] of lookback) {
    high = Math.max(high, rowHigh);
    low = Math.min(low, rowLow);
  }

  return { high, low };
}

export function filterBarsByRange(rows: BarRow[], range: ChartRange): BarRow[] {
  if (rows.length === 0 || range === "ALL") {
    return rows;
  }

  const lastDate = rows[rows.length - 1][0];
  const year = Number.parseInt(lastDate.slice(0, 4), 10);

  const takeLast = (count: number) => rows.slice(-count);

  switch (range) {
    case "1D":
      return takeLast(5);
    case "1W":
      return takeLast(10);
    case "1M":
      return takeLast(22);
    case "3M":
      return takeLast(66);
    case "YTD": {
      const start = `${year}-01-01`;
      const filtered = rows.filter(([date]) => date >= start);
      return filtered.length > 0 ? filtered : takeLast(22);
    }
    case "1Y":
      return takeLast(252);
    case "5Y":
      return takeLast(252 * 5);
    default:
      return rows;
  }
}

export function barsToLinePoints(rows: BarRow[]): Array<{ time: string; value: number }> {
  return rows.map(([date, , close]) => ({
    time: date,
    value: close,
  }));
}

export function rangePerformance(rows: BarRow[]): number {
  if (rows.length < 2) {
    return 0;
  }
  const first = rows[0][2];
  const last = rows[rows.length - 1][2];
  if (first === 0) {
    return 0;
  }
  return ((last - first) / first) * 100;
}
