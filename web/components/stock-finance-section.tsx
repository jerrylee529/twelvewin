import { getStockProfile } from "@/lib/api";
import type { ProfileResponse } from "@/lib/types";
import { formatPrice } from "@/lib/stock-format";

function MetricSection({
  title,
  points,
}: {
  title: string;
  points: Array<{ date: string; value: number }>;
}) {
  if (points.length === 0) {
    return null;
  }

  const max = Math.max(...points.map((point) => point.value), 1);
  const latest = points[points.length - 1];

  return (
    <section className="border-t border-outline-variant/40 py-8">
      <div className="mb-4 flex items-end justify-between gap-3">
        <h3 className="text-lg font-semibold text-on-surface">{title}</h3>
        <p className="text-sm tabular-nums text-on-surface-variant">
          {latest.date} · {formatPrice(latest.value)}
        </p>
      </div>
      <div className="flex h-28 items-end gap-1.5">
        {points.map((point) => (
          <div
            key={point.date}
            className="flex flex-1 flex-col items-center gap-2"
          >
            <div
              className="w-full rounded-sm bg-[#00C805]/35"
              style={{
                height: `${Math.max((point.value / max) * 100, 6)}%`,
              }}
              title={`${point.date}: ${point.value}`}
            />
            <span className="text-[10px] tabular-nums text-on-surface-variant">
              {point.date}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}

export async function StockFinanceSection({ code }: { code: string }) {
  const profile: ProfileResponse = await getStockProfile(code);

  return (
    <section className="mt-2">
      <h2 className="border-t border-outline-variant/40 pt-8 text-xl font-bold text-on-surface">
        财务指标
      </h2>
      <MetricSection title="净资产收益率" points={profile.avg_roe} />
      <MetricSection title="基本每股收益" points={profile.basic_eps} />
      <MetricSection title="毛利率" points={profile.gross_selling_rate} />
      <MetricSection
        title="扣非净利润同比增长"
        points={profile.np_atsopc_nrgal_yoy}
      />
    </section>
  );
}
