import { EmptyState, PageHeader } from "@/components/dashboard-shell";
import { RankingTable } from "@/components/ranking-table";
import { Chip } from "@/components/ui/primitives";
import { getPriceChange } from "@/lib/api";
import type { PriceChangePeriod } from "@/lib/types";

const PRICE_CHANGE_PERIODS: PriceChangePeriod[] = [
  "近一周",
  "近一月",
  "近三月",
  "近半年",
  "近一年",
];

function firstParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

function normalizePeriod(value: string | undefined): PriceChangePeriod {
  return PRICE_CHANGE_PERIODS.includes(value as PriceChangePeriod)
    ? (value as PriceChangePeriod)
    : "近一周";
}

export default async function PriceChangePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const days = normalizePeriod(firstParam(params.days));
  const low = firstParam(params.low) || "-30";
  const high = firstParam(params.high) || "0";
  const data = await getPriceChange(days, low, high);

  return (
    <>
      <PageHeader
        title="涨跌幅分析"
        description="按周期和涨跌幅区间筛选 A 股走势变化"
        updateTime={data.updateTime}
        badge={<Chip tone="bullish">技术面</Chip>}
      />

      <form
        action="/technical/filter"
        className="mb-4 flex flex-col gap-3 rounded-lg border border-on-surface/5 bg-surface-container-low p-3 sm:flex-row sm:items-end"
      >
        <label className="flex flex-col gap-1 text-xs text-on-surface-variant">
          周期
          <select
            name="days"
            defaultValue={days}
            className="trading-input min-w-32 rounded-sm text-on-surface"
          >
            {PRICE_CHANGE_PERIODS.map((period) => (
              <option key={period} value={period}>
                {period}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-on-surface-variant">
          最低涨跌幅(%)
          <input
            name="low"
            type="number"
            step="0.01"
            defaultValue={low}
            className="trading-input min-w-28 rounded-sm text-on-surface"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs text-on-surface-variant">
          最高涨跌幅(%)
          <input
            name="high"
            type="number"
            step="0.01"
            defaultValue={high}
            className="trading-input min-w-28 rounded-sm text-on-surface"
          />
        </label>
        <button
          type="submit"
          className="rounded-sm bg-primary-container px-4 py-2 text-xs font-medium text-on-primary-container transition hover:opacity-90"
        >
          提交
        </button>
      </form>

      {data.error && data.rows.length === 0 ? (
        <EmptyState
          message="暂无已发布的数据"
          hint="请先在服务端运行 python -m compute eod_all 生成并发布分析结果。"
        />
      ) : (
        <RankingTable rows={data.rows} />
      )}
    </>
  );
}
