import { StockPriceChart } from "@/components/stock-price-chart";
import { StockStatsSection } from "@/components/stock-stats-section";
import type { BarRow } from "@/lib/stock-format";
import type { BarsResponse, ResearchContextResponse } from "@/lib/types";

export function StockChartSection({
  code,
  name,
  initialQuot,
  initialBars,
  researchContext,
}: {
  code: string;
  name: string;
  initialQuot?: Record<string, string> | null;
  initialBars: BarsResponse;
  researchContext?: ResearchContextResponse;
}) {
  const rows = (initialBars.rows || []) as BarRow[];

  return (
    <>
      <section className="scroll-mt-16 mt-6">
        {rows.length > 0 ? (
          <StockPriceChart rows={rows} />
        ) : (
          <div className="rounded-lg border border-outline-variant/40 px-6 py-14 text-center">
            <p className="text-sm text-on-surface">暂无走势数据</p>
          </div>
        )}
      </section>

      <StockStatsSection
        code={code}
        name={name}
        bars={rows}
        updateTime={initialBars.updateTime}
        initialQuot={initialQuot}
        researchContext={researchContext}
      />
    </>
  );
}
