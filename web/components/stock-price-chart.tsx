"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  AreaSeries,
  CandlestickSeries,
  ColorType,
  createChart,
  CrosshairMode,
  HistogramSeries,
  type IChartApi,
  type ISeriesApi,
  type Time,
} from "lightweight-charts";
import {
  barVolume,
  barsToLinePoints,
  CHART_RANGES,
  filterBarsByRange,
  formatPrice,
  hasBarVolume,
  rangePerformance,
  type BarRow,
  type ChartRange,
} from "@/lib/stock-format";

/* Keep in sync with --bullish / --bearish tokens in globals.css */
const STOCK_UP = "#f6465d";
const STOCK_DOWN = "#0ecb81";

type ChartMode = "line" | "candle";

export function StockPriceChart({ rows }: { rows: BarRow[] }) {
  const [range, setRange] = useState<ChartRange>("1Y");
  const [mode, setMode] = useState<ChartMode>("line");
  const containerRef = useRef<HTMLDivElement | null>(null);
  const tooltipRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const priceSeriesRef = useRef<
    ISeriesApi<"Area"> | ISeriesApi<"Candlestick"> | null
  >(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);

  const filteredRows = useMemo(
    () => filterBarsByRange(rows, range),
    [rows, range],
  );
  const showVolume = useMemo(() => hasBarVolume(filteredRows), [filteredRows]);

  const isUp = useMemo(() => rangePerformance(filteredRows) >= 0, [filteredRows]);
  const lineColor = isUp ? STOCK_UP : STOCK_DOWN;
  const areaTop = isUp ? "rgba(246, 70, 93, 0.22)" : "rgba(14, 203, 129, 0.22)";
  const areaBottom = "rgba(0, 0, 0, 0)";

  useEffect(() => {
    if (!containerRef.current || !tooltipRef.current) {
      return;
    }

    const fontFamily =
      getComputedStyle(document.documentElement)
        .getPropertyValue("--font-sans")
        .trim() || "system-ui, sans-serif";

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#8b95b8",
        fontFamily,
        fontSize: 11,
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { color: "rgba(139, 149, 184, 0.12)" },
      },
      width: containerRef.current.clientWidth,
      height: showVolume ? 380 : 320,
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: { top: 0.12, bottom: showVolume ? 0.32 : 0.08 },
      },
      timeScale: {
        borderVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
      crosshair: {
        mode: CrosshairMode.Magnet,
        vertLine: { color: "rgba(139, 149, 184, 0.35)", width: 1 },
        horzLine: { color: "rgba(139, 149, 184, 0.35)", width: 1 },
      },
      handleScroll: true,
      handleScale: true,
    });

    chartRef.current = chart;

    const observer = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    });
    observer.observe(containerRef.current);

    chart.subscribeCrosshairMove((param) => {
      const tooltip = tooltipRef.current;
      const container = containerRef.current;
      if (!tooltip || !container) {
        return;
      }

      if (!param.time || !param.point || param.point.x < 0 || param.point.y < 0) {
        tooltip.style.display = "none";
        return;
      }

      const date = String(param.time);
      const row = filteredRows.find(([tradeDate]) => tradeDate === date);
      if (!row) {
        tooltip.style.display = "none";
        return;
      }

      const [, open, close, low, high] = row;
      const volume = barVolume(row);
      const changePct = open !== 0 ? ((close - open) / open) * 100 : 0;
      const tone = close >= open ? STOCK_UP : STOCK_DOWN;

      tooltip.style.display = "block";
      tooltip.style.left = `${Math.min(param.point.x + 12, container.clientWidth - 160)}px`;
      tooltip.style.top = "8px";
      tooltip.innerHTML = `
        <p style="font-size:11px;color:#8b95b8;margin:0 0 4px">${date}</p>
        <p style="font-size:13px;font-weight:600;color:${tone};margin:0">¥${formatPrice(close)}</p>
        <p style="font-size:11px;color:#8b95b8;margin:4px 0 0">O ${formatPrice(open)} · H ${formatPrice(high)} · L ${formatPrice(low)}</p>
        <p style="font-size:11px;color:#8b95b8;margin:2px 0 0">${changePct >= 0 ? "+" : ""}${changePct.toFixed(2)}%</p>
        ${volume > 0 ? `<p style="font-size:11px;color:#8b95b8;margin:2px 0 0">Vol ${Math.round(volume).toLocaleString("zh-CN")}</p>` : ""}
      `;
    });

    return () => {
      observer.disconnect();
      chart.remove();
      chartRef.current = null;
      priceSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, [filteredRows, showVolume]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) {
      return;
    }

    if (priceSeriesRef.current) {
      chart.removeSeries(priceSeriesRef.current);
      priceSeriesRef.current = null;
    }
    if (volumeSeriesRef.current) {
      chart.removeSeries(volumeSeriesRef.current);
      volumeSeriesRef.current = null;
    }

    if (mode === "candle") {
      const series = chart.addSeries(CandlestickSeries, {
        upColor: STOCK_UP,
        downColor: STOCK_DOWN,
        borderUpColor: STOCK_UP,
        borderDownColor: STOCK_DOWN,
        wickUpColor: STOCK_UP,
        wickDownColor: STOCK_DOWN,
        priceLineVisible: false,
      });
      series.setData(
        filteredRows.map(([date, open, close, low, high]) => ({
          time: date as Time,
          open,
          close,
          low,
          high,
        })),
      );
      priceSeriesRef.current = series;
    } else {
      const series = chart.addSeries(AreaSeries, {
        lineColor,
        topColor: areaTop,
        bottomColor: areaBottom,
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: true,
        crosshairMarkerVisible: true,
      });
      series.setData(barsToLinePoints(filteredRows));
      priceSeriesRef.current = series;
    }

    if (showVolume) {
      const volumeSeries = chart.addSeries(HistogramSeries, {
        priceFormat: { type: "volume" },
        priceScaleId: "",
      });
      volumeSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.82, bottom: 0 },
      });
      volumeSeries.setData(
        filteredRows.map(([date, open, close, , , volume]) => ({
          time: date as Time,
          value: volume ?? 0,
          color:
            close >= open
              ? "rgba(246, 70, 93, 0.45)"
              : "rgba(14, 203, 129, 0.45)",
        })),
      );
      volumeSeriesRef.current = volumeSeries;
    }

    chart.timeScale().fitContent();
  }, [filteredRows, mode, lineColor, areaTop, areaBottom, showVolume]);

  return (
    <div className="relative w-full">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {CHART_RANGES.map((item) => {
            const active = item === range;
            return (
              <button
                key={item}
                type="button"
                onClick={() => setRange(item)}
                className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                  active
                    ? "bg-on-surface text-surface"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                {item}
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-1 rounded-full border border-outline-variant/40 p-0.5">
          {(["line", "candle"] as ChartMode[]).map((item) => {
            const active = item === mode;
            return (
              <button
                key={item}
                type="button"
                onClick={() => setMode(item)}
                className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
                  active
                    ? "bg-on-surface text-surface"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                {item === "line" ? "折线" : "K线"}
              </button>
            );
          })}
        </div>
      </div>

      <div
        ref={tooltipRef}
        className="pointer-events-none absolute z-10 hidden min-w-[140px] rounded-sm border border-outline-variant/50 bg-surface-container-high/95 px-3 py-2 shadow-sm backdrop-blur-sm"
      />

      <div ref={containerRef} className="mt-2 w-full" />
    </div>
  );
}
