"use client";

import { useStockQuote } from "@/components/stock-quote-provider";
import {
  compute52WeekRange,
  formatMarketCap,
  formatPercent,
  formatPrice,
  formatVolume,
  parseNumber,
  type BarRow,
} from "@/lib/stock-format";
import type { ResearchContextResponse } from "@/lib/types";

function StatItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-outline-variant/40 py-2.5">
      <dt className="text-sm text-on-surface-variant">{label}</dt>
      <dd className="text-right text-sm font-medium tabular-nums text-on-surface">
        {value}
      </dd>
    </div>
  );
}

function StatGroup({
  title,
  items,
}: {
  title: string;
  items: Array<{ label: string; value: string }>;
}) {
  return (
    <div>
      <h3 className="mb-1 text-sm font-semibold text-on-surface">{title}</h3>
      <dl>
        {items.map((item) => (
          <StatItem key={item.label} label={item.label} value={item.value} />
        ))}
      </dl>
    </div>
  );
}

export function StockStatsSection({
  code,
  bars,
  updateTime,
  initialQuot,
  researchContext,
}: {
  code: string;
  name: string;
  bars: BarRow[];
  updateTime?: string | null;
  initialQuot?: Record<string, string> | null;
  researchContext?: ResearchContextResponse;
}) {
  const { data } = useStockQuote();
  const quot = data?.quot ?? initialQuot;
  const settlement = parseNumber(quot?.settlement);
  const week52 = compute52WeekRange(bars);
  const fundamentals = researchContext?.fundamentals;

  const valuationStats = [
    { label: "总市值", value: formatMarketCap(quot?.mktcap) },
    {
      label: "流通市值",
      value:
        quot?.nmc
          ? formatMarketCap(quot.nmc)
          : fundamentals?.float_market_cap != null
            ? formatMarketCap(String(fundamentals.float_market_cap))
            : "—",
    },
    {
      label: "市盈率",
      value:
        quot?.per
          ? formatPrice(parseNumber(quot.per))
          : fundamentals?.pe_ttm != null
            ? formatPrice(fundamentals.pe_ttm)
            : "—",
    },
    {
      label: "市净率",
      value:
        quot?.pb
          ? formatPrice(parseNumber(quot.pb))
          : fundamentals?.pb_lf != null
            ? formatPrice(fundamentals.pb_lf)
            : "—",
    },
    {
      label: "净资产收益率",
      value:
        fundamentals?.roe != null ? formatPercent(fundamentals.roe) : "—",
    },
    {
      label: "股息率",
      value:
        fundamentals?.dividend_yield != null
          ? formatPercent(fundamentals.dividend_yield)
          : "—",
    },
  ];

  const tradingStats = [
    { label: "成交量", value: formatVolume(quot?.volume) },
    ...(quot?.turnoverratio
      ? [
          {
            label: "换手率",
            value: formatPercent(parseNumber(quot.turnoverratio), 2),
          },
        ]
      : []),
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
    <section id="stock-stats" className="scroll-mt-16">
      {updateTime ? (
        <p className="mt-3 text-xs text-on-surface-variant">
          数据截至 {updateTime}
        </p>
      ) : null}

      <div className="mt-8 border-t border-outline-variant/40 pt-8">
        <h2 className="text-xl font-bold text-on-surface">{code} 关键指标</h2>
        <div className="mt-4 grid gap-8 sm:grid-cols-2">
          <StatGroup title="估值与回报" items={valuationStats} />
          <StatGroup title="交易与区间" items={tradingStats} />
        </div>
      </div>
    </section>
  );
}
