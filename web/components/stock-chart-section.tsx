import { getStockBars } from "@/lib/api";
import { StockLineChart } from "@/components/stock-line-chart";
import { StockStatsSection } from "@/components/stock-stats-section";
import type { BarRow } from "@/lib/stock-format";

export async function StockChartSection({
  code,
  name,
  initialQuot,
}: {
  code: string;
  name: string;
  initialQuot?: Record<string, string> | null;
}) {
  const bars = await getStockBars(code);
  const rows = bars.rows as BarRow[];

  return (
    <>
      <section className="mt-6">
        {rows.length > 0 ? (
          <StockLineChart rows={rows} />
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
        updateTime={bars.updateTime}
        initialQuot={initialQuot}
      />
    </>
  );
}
