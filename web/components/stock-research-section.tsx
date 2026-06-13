import Link from "next/link";

import type { ResearchContextResponse } from "@/lib/types";
import { RANKING_DISPLAY_META, TECHNICAL_META, type TechnicalKey } from "@/lib/types";
import { formatPercent, formatPrice } from "@/lib/stock-format";

function formatComparisonValue(
  value: number | null | undefined,
  format: "number" | "percent",
): string {
  if (value == null) {
    return "—";
  }
  return format === "percent" ? formatPercent(value) : formatPrice(value);
}

function DeltaBadge({
  discount,
  higherIsBetter = false,
}: {
  discount?: number | null;
  higherIsBetter?: boolean;
}) {
  if (discount == null || !Number.isFinite(discount)) {
    return <span className="text-on-surface-variant">—</span>;
  }

  const above = discount > 0;
  const favorable = higherIsBetter ? above : above;
  const tone = favorable ? "text-bullish" : "text-bearish";
  const prefix = higherIsBetter
    ? above
      ? "高于"
      : "低于"
    : above
      ? "低于"
      : "高于";
  const magnitude = formatPercent(Math.abs(discount));

  return (
    <span className={`text-xs font-medium tabular-nums ${tone}`}>
      {prefix}行业 {magnitude}
    </span>
  );
}

function SignalBadge({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="rounded-full border border-outline-variant/50 bg-surface-container-low px-3 py-1 text-xs text-on-surface transition hover:border-outline hover:bg-surface-container-high"
    >
      {label}
    </Link>
  );
}

export function StockResearchSection({
  context,
}: {
  context: ResearchContextResponse;
}) {
  const benchmark = context.industry_benchmark;
  const fundamentals = context.fundamentals;
  const signals = context.technical_signals || [];
  const rankings = context.rankings || {};
  const peers = context.cluster_peers || [];

  const comparisonRows = [
    {
      label: "市盈率 (TTM)",
      stockValue: fundamentals?.pe_ttm,
      industryValue: benchmark?.median_pe_ttm,
      discount: fundamentals?.pe_discount_to_industry,
      format: "number" as const,
      higherIsBetter: false,
    },
    {
      label: "市净率 (LF)",
      stockValue: fundamentals?.pb_lf,
      industryValue: benchmark?.median_pb_lf,
      discount: fundamentals?.pb_discount_to_industry,
      format: "number" as const,
      higherIsBetter: false,
    },
    {
      label: "净资产收益率",
      stockValue: fundamentals?.roe,
      industryValue: benchmark?.median_roe,
      discount:
        fundamentals?.roe != null && benchmark?.median_roe
          ? ((fundamentals.roe - benchmark.median_roe) /
              benchmark.median_roe) *
            100
          : null,
      format: "percent" as const,
      higherIsBetter: true,
    },
    {
      label: "股息率",
      stockValue: fundamentals?.dividend_yield,
      industryValue: benchmark?.median_dividend_yield,
      discount:
        fundamentals?.dividend_yield != null &&
        benchmark?.median_dividend_yield
          ? ((fundamentals.dividend_yield - benchmark.median_dividend_yield) /
              benchmark.median_dividend_yield) *
            100
          : null,
      format: "percent" as const,
      higherIsBetter: true,
    },
  ].filter(
    (row) => row.stockValue != null || row.industryValue != null,
  );

  const hasIndustry = comparisonRows.length > 0;
  const hasSignals = signals.length > 0 || Object.keys(rankings).length > 0;
  const showPeColumn = peers.some((peer) => peer.pe != null);
  const showPbColumn = peers.some((peer) => peer.pb != null);
  const hasPeers = peers.length > 0;

  if (!hasIndustry && !hasSignals && !hasPeers) {
    return null;
  }

  return (
    <section className="scroll-mt-16 border-t border-outline-variant/40 pt-8">
      <h2 className="text-xl font-bold text-on-surface">研究概览</h2>
      {context.industry ? (
        <p className="mt-2 text-sm text-on-surface-variant">
          所属行业：{context.industry}
          {context.data_as_of ? ` · 数据截至 ${context.data_as_of}` : null}
        </p>
      ) : null}

      {hasIndustry ? (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-on-surface">行业对比</h3>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[520px] text-sm">
              <thead>
                <tr className="border-b border-outline-variant/40 text-left text-xs text-on-surface-variant">
                  <th className="pb-2 pr-4 font-medium">指标</th>
                  <th className="pb-2 pr-4 font-medium">个股</th>
                  <th className="pb-2 pr-4 font-medium">行业中位</th>
                  <th className="pb-2 font-medium">相对行业</th>
                </tr>
              </thead>
              <tbody>
                {comparisonRows.map((row) => (
                  <tr
                    key={row.label}
                    className="border-b border-outline-variant/30 last:border-0"
                  >
                    <td className="py-2.5 pr-4 text-on-surface-variant">
                      {row.label}
                    </td>
                    <td className="py-2.5 pr-4 font-medium tabular-nums text-on-surface">
                      {formatComparisonValue(row.stockValue, row.format)}
                    </td>
                    <td className="py-2.5 pr-4 tabular-nums text-on-surface-variant">
                      {formatComparisonValue(row.industryValue, row.format)}
                    </td>
                    <td className="py-2.5">
                      <DeltaBadge
                        discount={row.discount}
                        higherIsBetter={row.higherIsBetter}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {hasSignals ? (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-on-surface">信号与排名</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {signals.map((key) => {
              const meta = TECHNICAL_META[key as TechnicalKey];
              return (
                <SignalBadge
                  key={key}
                  href={`/technical/${key}`}
                  label={meta?.title || key}
                />
              );
            })}
            {Object.entries(rankings).map(([key, rank]) => {
              const meta = RANKING_DISPLAY_META[key];
              const href =
                key === "value" ? "/fundamentals" : `/fundamentals?metric=${key}`;
              return (
                <SignalBadge
                  key={key}
                  href={href}
                  label={`${meta?.title || key} #${rank}`}
                />
              );
            })}
          </div>
        </div>
      ) : null}

      {hasPeers ? (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-on-surface">同行业个股</h3>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[320px] text-sm">
              <thead>
                <tr className="border-b border-outline-variant/40 text-left text-xs text-on-surface-variant">
                  <th className="pb-2 pr-4 font-medium">代码</th>
                  <th className="pb-2 pr-4 font-medium">名称</th>
                  {showPeColumn ? (
                    <th className="pb-2 pr-4 font-medium">PE</th>
                  ) : null}
                  {showPbColumn ? (
                    <th className="pb-2 font-medium">PB</th>
                  ) : null}
                </tr>
              </thead>
              <tbody>
                {peers.map((peer) => (
                  <tr
                    key={peer.code}
                    className="border-b border-outline-variant/30 last:border-0"
                  >
                    <td className="py-2.5 pr-4">
                      <Link
                        href={`/stock/${peer.code}`}
                        className="tabular-nums text-on-surface transition hover:text-primary"
                      >
                        {peer.code}
                      </Link>
                    </td>
                    <td className="py-2.5 pr-4 text-on-surface">{peer.name}</td>
                    {showPeColumn ? (
                      <td className="py-2.5 pr-4 tabular-nums text-on-surface-variant">
                        {peer.pe != null ? formatPrice(peer.pe) : "—"}
                      </td>
                    ) : null}
                    {showPbColumn ? (
                      <td className="py-2.5 tabular-nums text-on-surface-variant">
                        {peer.pb != null ? formatPrice(peer.pb) : "—"}
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </section>
  );
}
