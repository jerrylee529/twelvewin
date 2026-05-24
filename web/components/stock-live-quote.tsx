"use client";

import { useStockQuote } from "@/components/stock-quote-provider";
import {
  formatPercent,
  formatPrice,
  parseNumber,
} from "@/lib/stock-format";
import { StockQuoteSkeleton } from "@/components/stock-skeletons";

export function StockLiveQuote({ code }: { code: string }) {
  const { data, loading, error } = useStockQuote();
  const quot = data?.quot;
  const quotSource = data?.quot_source;
  const name = quot?.name || code;
  const trade = parseNumber(quot?.trade);
  const settlement = parseNumber(quot?.settlement);
  const changePercent = parseNumber(quot?.changepercent);
  const changeAmount =
    settlement > 0 ? trade - settlement : (trade * changePercent) / 100;
  const isUp = changeAmount >= 0;
  const toneClass = isUp ? "text-bullish" : "text-bearish";

  if (loading && !quot) {
    return <StockQuoteSkeleton />;
  }

  return (
    <header className="pt-2">
      <h1 className="text-[32px] font-bold leading-tight tracking-tight text-on-surface">
        {name}
      </h1>
      <p className="mt-1 text-sm text-on-surface-variant">{code}</p>

      {quot ? (
        <div className="mt-4">
          <p
            className={`text-[44px] font-bold leading-none tabular-nums tracking-tight ${toneClass}`}
          >
            ¥{formatPrice(trade)}
          </p>
          <p
            className={`mt-2 text-base font-medium tabular-nums ${toneClass}`}
          >
            {changeAmount > 0 ? "+" : ""}
            {formatPrice(changeAmount)} ({formatPercent(changePercent)})
          </p>
        </div>
      ) : (
        <p className="mt-4 text-sm text-on-surface-variant">
          {error ? "行情加载失败" : "暂无行情数据"}
        </p>
      )}

      {quot && quotSource === "daily_bar" ? (
        <p className="mt-2 text-xs text-on-surface-variant">
          基于最新收盘数据（Redis 实时行情未就绪）
        </p>
      ) : null}
    </header>
  );
}
