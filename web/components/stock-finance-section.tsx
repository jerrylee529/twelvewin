import { getStockProfile } from "@/lib/api";
import type { ProfileResponse } from "@/lib/types";
import { formatPercent, formatPrice } from "@/lib/stock-format";

const CHART_BAR_MAX_PX = 72;
const CHART_PLOT_HEIGHT_PX = 112;

type MetricFormat = "percent" | "price";

function formatMetricValue(value: number, format: MetricFormat): string {
  return format === "percent" ? formatPercent(value) : formatPrice(value);
}

function formatAxisValue(value: number, format: MetricFormat): string {
  if (format === "percent") {
    return `${value.toFixed(value >= 10 ? 0 : 1)}%`;
  }
  return formatPrice(value, value >= 10 ? 1 : 2);
}

function metricTone(value: number) {
  return value >= 0
    ? { bar: "bg-[#FF5000]/80", text: "text-[#FF6A3D]" }
    : { bar: "bg-[#00C805]/80", text: "text-[#2EEA5A]" };
}

function MetricSection({
  title,
  points,
  format = "price",
}: {
  title: string;
  points: Array<{ date: string; value: number }>;
  format?: MetricFormat;
}) {
  if (points.length === 0) {
    return null;
  }

  const maxAbs = Math.max(...points.map((point) => Math.abs(point.value)), 1e-9);
  const axisMax = Math.max(...points.map((point) => point.value), 0);
  const axisMid = axisMax / 2;
  const latest = points[points.length - 1];

  return (
    <section className="border-t border-outline-variant/40 py-8">
      <div className="mb-4 flex items-end justify-between gap-3">
        <h3 className="text-lg font-semibold text-on-surface">{title}</h3>
        <p className="text-sm tabular-nums text-on-surface-variant">
          {latest.date} · {formatMetricValue(latest.value, format)}
        </p>
      </div>

      <div className="rounded-sm border border-outline-variant/50 bg-surface-container-low/20 px-3 py-3">
        <div className="flex gap-2">
          <div
            className="flex w-11 shrink-0 flex-col justify-between py-1 text-right text-[10px] tabular-nums text-on-surface-variant"
            style={{ height: `${CHART_PLOT_HEIGHT_PX}px` }}
          >
            <span>{formatAxisValue(axisMax, format)}</span>
            {axisMax > 0 ? (
              <span>{formatAxisValue(axisMid, format)}</span>
            ) : null}
            <span>{format === "percent" ? "0%" : "0"}</span>
          </div>

          <div className="min-w-0 flex-1">
            <div
              className="relative border-l border-b border-outline-variant/60"
              style={{ height: `${CHART_PLOT_HEIGHT_PX}px` }}
            >
              <div className="relative flex h-full items-end gap-2 px-2 pb-0">
                {points.map((point) => {
                  const barHeight = Math.max(
                    (Math.abs(point.value) / maxAbs) * CHART_BAR_MAX_PX,
                    4,
                  );
                  const valueLabel = formatMetricValue(point.value, format);
                  const tone = metricTone(point.value);

                  return (
                    <div
                      key={point.date}
                      className="flex min-w-0 flex-1 flex-col items-center justify-end gap-1"
                    >
                      <span
                        className={`max-w-full truncate text-[10px] font-medium tabular-nums ${tone.text}`}
                        title={valueLabel}
                      >
                        {valueLabel}
                      </span>
                      <div
                        className={`w-6 shrink-0 rounded-sm sm:w-7 ${tone.bar}`}
                        style={{ height: `${barHeight}px` }}
                        title={`${point.date}: ${valueLabel}`}
                      />
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="mt-1 flex gap-2 px-2 pt-1.5">
              {points.map((point) => (
                <span
                  key={point.date}
                  className="min-w-0 flex-1 text-center text-[10px] tabular-nums text-on-surface-variant"
                >
                  {point.date}
                </span>
              ))}
            </div>
          </div>
        </div>
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
      <MetricSection title="净资产收益率" points={profile.avg_roe} format="percent" />
      <MetricSection title="基本每股收益" points={profile.basic_eps} format="price" />
      <MetricSection
        title="毛利率"
        points={profile.gross_selling_rate}
        format="percent"
      />
      <MetricSection
        title="扣非净利润同比增长"
        points={profile.np_atsopc_nrgal_yoy}
        format="percent"
      />
    </section>
  );
}
