"use client";

import { useStockQuote } from "@/components/stock-quote-provider";
import {
  compute52WeekRange,
  formatMarketCap,
  formatPercent,
  formatPrice,
  parseNumber,
  type BarRow,
} from "@/lib/stock-format";

export function StockAboutSection({
  code,
  bars,
}: {
  code: string;
  bars: BarRow[];
}) {
  const { data } = useStockQuote();
  const quot = data?.quot;
  const name = quot?.name || code;
  const trade = parseNumber(quot?.trade);
  const week52 = compute52WeekRange(bars);

  const snapshotParts = [
    `${name}（${code}）当前价格为 ¥${trade > 0 ? formatPrice(trade) : "—"}。`,
    quot?.mktcap
      ? `公司总市值约 ${formatMarketCap(quot.mktcap)}。`
      : null,
    quot?.per ? `市盈率为 ${formatPrice(parseNumber(quot.per))}。` : null,
    week52.high > 0 && week52.low > 0
      ? `过去 52 周股价区间 ${formatPrice(week52.low)} – ${formatPrice(week52.high)}。`
      : null,
  ].filter(Boolean);

  return (
    <section className="mt-10 border-t border-outline-variant/40 py-8">
      <h2 className="text-xl font-bold text-on-surface">关于 {code}</h2>
      <p className="mt-4 text-sm leading-7 text-on-surface-variant">
        {snapshotParts.join(" ")}
      </p>
      <dl className="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-xs text-on-surface-variant">公司名称</dt>
          <dd className="mt-1 text-sm font-medium text-on-surface">{name}</dd>
        </div>
        <div>
          <dt className="text-xs text-on-surface-variant">股票代码</dt>
          <dd className="mt-1 text-sm font-medium tabular-nums text-on-surface">
            {code}
          </dd>
        </div>
        {quot?.turnoverratio ? (
          <div>
            <dt className="text-xs text-on-surface-variant">换手率</dt>
            <dd className="mt-1 text-sm font-medium tabular-nums text-on-surface">
              {formatPercent(parseNumber(quot.turnoverratio), 2)}
            </dd>
          </div>
        ) : null}
        {quot?.nmc ? (
          <div>
            <dt className="text-xs text-on-surface-variant">流通市值</dt>
            <dd className="mt-1 text-sm font-medium tabular-nums text-on-surface">
              {formatMarketCap(quot.nmc)}
            </dd>
          </div>
        ) : null}
      </dl>
    </section>
  );
}
