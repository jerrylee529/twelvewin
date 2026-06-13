"use client";

import { useEffect, useRef, useState } from "react";
import { useStockQuote } from "@/components/stock-quote-provider";
import {
  formatPercent,
  formatPrice,
  parseNumber,
} from "@/lib/stock-format";

/** Background flash on price change, A-share red-up / green-down. */
function usePriceFlash(price: number | null) {
  const previousRef = useRef<number | null>(null);
  const [flash, setFlash] = useState<{ dir: "up" | "down"; id: number } | null>(
    null,
  );

  useEffect(() => {
    if (price == null) {
      return;
    }
    const previous = previousRef.current;
    previousRef.current = price;
    if (previous == null || previous === price) {
      return;
    }
    setFlash({ dir: price > previous ? "up" : "down", id: Date.now() });
  }, [price]);

  return flash;
}

/** Live price overlay; H1 is rendered server-side in StockPageHeader. */
export function StockLivePrice() {
  const { data, loading, error } = useStockQuote();
  const quot = data?.quot;
  const quotSource = data?.quot_source;
  const flash = usePriceFlash(quot ? parseNumber(quot.trade) : null);

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
        key={flash?.id}
        className={`inline-block rounded-sm text-[44px] font-bold leading-none tabular-nums tracking-tight ${toneClass} ${
          flash ? (flash.dir === "up" ? "flash-up" : "flash-down") : ""
        }`}
      >
        ¥{formatPrice(trade)}
      </p>
      <p className={`mt-2 text-base font-medium tabular-nums ${toneClass}`}>
        {changeAmount > 0 ? "+" : ""}
        {formatPrice(changeAmount)} ({formatPercent(changePercent)})
      </p>
      {quotSource === "daily_bar" ? (
        <p className="mt-2 text-xs text-on-surface-variant">
          收盘价 · {quot.update_time || "—"}
        </p>
      ) : null}
    </div>
  );
}
