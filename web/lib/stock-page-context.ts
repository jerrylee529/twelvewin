import { cache } from "react";

import {
  getStockBars,
  getStockQuote,
  getStockResearchContext,
  STOCK_BARS_MAX_DAYS,
} from "@/lib/api";
import { buildStockDescription } from "@/lib/seo";
import type { BarsResponse, QuoteResponse, ResearchContextResponse } from "@/lib/types";
import { compute52WeekRange, parseNumber, type BarRow } from "@/lib/stock-format";

export type StockPageContext = {
  quotePayload: QuoteResponse;
  barsPayload: BarsResponse;
  researchContext: ResearchContextResponse;
  name: string;
  description: string;
  updateTime: string | null;
  rows: BarRow[];
};

export const loadStockPageContext = cache(async (code: string): Promise<StockPageContext> => {
  const [quotePayload, barsPayload, researchContext] = await Promise.all([
    getStockQuote(code).catch(() => ({ quot: null, quot_source: null })),
    getStockBars(code, { days: STOCK_BARS_MAX_DAYS, includeQuote: true }).catch(() => ({
      rows: [],
      updateTime: null,
      error: "failed to load bars",
    })),
    getStockResearchContext(code).catch(() => ({ error: "failed to load context" })),
  ]);

  const quot = quotePayload.quot;
  const rows = (barsPayload.rows || []) as BarRow[];
  const week52 = compute52WeekRange(rows);
  const name =
    quot?.name ||
    ("name" in researchContext ? researchContext.name : null) ||
    code;

  return {
    quotePayload,
    barsPayload,
    researchContext,
    name,
    description: buildStockDescription({
      code,
      name,
      trade: parseNumber(quot?.trade) || undefined,
      pe: parseNumber(quot?.per) || undefined,
      week52Low: week52.low || undefined,
      week52High: week52.high || undefined,
    }),
    updateTime: barsPayload.updateTime || quot?.update_time || null,
    rows,
  };
});

export function isStockPageMissing(context: StockPageContext): boolean {
  if (context.researchContext.error === "invalid stock code") {
    return true;
  }
  const hasQuote = Boolean(context.quotePayload.quot);
  const hasBars = context.rows.length > 0;
  return !hasQuote && !hasBars;
}
