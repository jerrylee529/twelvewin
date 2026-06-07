"use client";

import { useStockQuote } from "@/components/stock-quote-provider";
import {
  compute52WeekRange,
  formatMarketCap,
  formatPrice,
  formatVolume,
  parseNumber,
  type BarRow,
} from "@/lib/stock-format";
import { StockSeoAbout } from "@/components/stock-seo-about";

function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-outline-variant/40 py-3">
      <dt className="text-sm text-on-surface-variant">{label}</dt>
      <dd className="text-right text-sm font-medium tabular-nums text-on-surface">
        {value}
      </dd>
    </div>
  );
}

export function StockStatsSection({
  code,
  name,
  bars,
  updateTime,
  initialQuot,
}: {
  code: string;
  name: string;
  bars: BarRow[];
  updateTime?: string | null;
  initialQuot?: Record<string, string> | null;
}) {
  const { data } = useStockQuote();
  const quot = data?.quot ?? initialQuot;
  const settlement = parseNumber(quot?.settlement);
  const week52 = compute52WeekRange(bars);

  const stats = [
    { label: "总市值", value: formatMarketCap(quot?.mktcap) },
    {
      label: "市盈率",
      value: quot?.per ? formatPrice(parseNumber(quot.per)) : "—",
    },
    {
      label: "市净率",
      value: quot?.pb ? formatPrice(parseNumber(quot.pb)) : "—",
    },
    { label: "成交量", value: formatVolume(quot?.volume) },
    {
      label: "今日最高",
      value: quot?.high ? formatPrice(parseNumber(quot.high)) : "—",
    },
    {
      label: "今日最低",
      value: quot?.low ? formatPrice(parseNumber(quot.low)) : "—",
    },
    {
      label: "今开",
      value: quot?.open ? formatPrice(parseNumber(quot.open)) : "—",
    },
    {
      label: "昨收",
      value: settlement > 0 ? formatPrice(settlement) : "—",
    },
    {
      label: "52 周最高",
      value: week52.high > 0 ? formatPrice(week52.high) : "—",
    },
    {
      label: "52 周最低",
      value: week52.low > 0 ? formatPrice(week52.low) : "—",
    },
  ];

  return (
    <>
      {updateTime ? (
        <p className="mt-3 text-xs text-on-surface-variant">
          数据截至 {updateTime}
        </p>
      ) : null}

      <div className="mt-10 grid gap-8 lg:grid-cols-2 lg:items-start">
        <section>
          <h2 className="text-xl font-bold text-on-surface">{code} 关键指标</h2>
          <dl className="mt-2">
            {stats.map((item) => (
              <StatItem key={item.label} label={item.label} value={item.value} />
            ))}
          </dl>
        </section>

        <StockSeoAbout code={code} name={name} quot={quot} bars={bars} />
      </div>
    </>
  );
}
