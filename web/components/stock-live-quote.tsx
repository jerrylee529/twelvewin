"use client";

import { useStockQuote } from "@/components/stock-quote-provider";
import {
  formatPercent,
  formatPrice,
  parseNumber,
} from "@/lib/stock-format";

/** Live price overlay; H1 is rendered server-side in StockPageHeader. */
export function StockLivePrice() {
  const { data, loading, error } = useStockQuote();
  const quot = data?.quot;
  const quotSource = data?.quot_source;

  if (loading && !quot) {
    return null;
  }

  if (!quot) {
    if (error) {
      return (
        <p className="mt-4 text-sm text-on-surface-variant">行情加载失败</p>
      );
    }
    return null;
  }

  const trade = parseNumber(quot.trade);
  const settlement = parseNumber(quot.settlement);
  const changePercent = parseNumber(quot.changepercent);
  const changeAmount =
    settlement > 0 ? trade - settlement : (trade * changePercent) / 100;
  const isUp = changeAmount >= 0;
  const toneClass = isUp ? "text-bullish" : "text-bearish";

  return (
    <div className="mt-4" aria-live="polite">
      <p
        className={`text-[44px] font-bold leading-none tabular-nums tracking-tight ${toneClass}`}
      >
        ¥{formatPrice(trade)}
      </p>
      <p className={`mt-2 text-base font-medium tabular-nums ${toneClass}`}>
        {changeAmount > 0 ? "+" : ""}
        {formatPrice(changeAmount)} ({formatPercent(changePercent)})
      </p>
      {quotSource === "daily_bar" ? (
        <p className="mt-2 text-xs text-on-surface-variant">
          基于最新收盘数据（Redis 实时行情未就绪）
        </p>
      ) : null}
    </div>
  );
}
