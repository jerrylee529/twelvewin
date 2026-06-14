import { StockPriceChart } from "@/components/stock-price-chart";
import type { BarRow } from "@/lib/stock-format";
import type { BarsResponse } from "@/lib/types";

export function StockChartSection({
  initialBars,
}: {
  initialBars: BarsResponse;
}) {
  const rows = (initialBars.rows || []) as BarRow[];

  return (
    <section className="scroll-mt-16 mt-6">
      {rows.length > 0 ? (
        <StockPriceChart rows={rows} />
      ) : (
        <div className="rounded-lg border border-outline-variant/40 px-6 py-14 text-center">
          <p className="text-sm text-on-surface">暂无走势数据</p>
        </div>
      )}
    </section>
  );
}
