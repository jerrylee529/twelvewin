"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  AreaSeries,
  ColorType,
  createChart,
  type IChartApi,
  type ISeriesApi,
} from "lightweight-charts";
import {
  barsToLinePoints,
  CHART_RANGES,
  filterBarsByRange,
  rangePerformance,
  type BarRow,
  type ChartRange,
} from "@/lib/stock-format";

/* Keep in sync with --bullish / --bearish tokens in globals.css */
const STOCK_UP = "#f6465d";
const STOCK_DOWN = "#0ecb81";

export function StockLineChart({ rows }: { rows: BarRow[] }) {
  const [range, setRange] = useState<ChartRange>("1Y");
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Area"> | null>(null);

  const filteredRows = useMemo(
    () => filterBarsByRange(rows, range),
    [rows, range],
  );

  const isUp = useMemo(() => rangePerformance(filteredRows) >= 0, [filteredRows]);
  const lineColor = isUp ? STOCK_UP : STOCK_DOWN;
  const areaTop = isUp ? "rgba(246, 70, 93, 0.22)" : "rgba(14, 203, 129, 0.22)";
  const areaBottom = "rgba(0, 0, 0, 0)";

  useEffect(() => {
    if (!containerRef.current) {
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
        horzLines: { visible: false },
      },
      width: containerRef.current.clientWidth,
      height: 320,
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: { top: 0.12, bottom: 0.08 },
      },
      timeScale: {
        borderVisible: false,
        fixLeftEdge: true,
        fixRightEdge: true,
      },
      crosshair: {
        vertLine: { visible: false },
        horzLine: { visible: false },
      },
      handleScroll: false,
      handleScale: false,
    });

    const series = chart.addSeries(AreaSeries, {
      lineColor: STOCK_UP,
      topColor: areaTop,
      bottomColor: areaBottom,
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
      crosshairMarkerVisible: false,
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const observer = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    });
    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current) {
      return;
    }

    seriesRef.current.applyOptions({
      lineColor,
      topColor: areaTop,
      bottomColor: areaBottom,
    });

    seriesRef.current.setData(barsToLinePoints(filteredRows));
    chartRef.current?.timeScale().fitContent();
  }, [filteredRows, lineColor, areaTop, areaBottom]);

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-1">
        {CHART_RANGES.map((item) => {
          const active = item === range;
          return (
            <button
              key={item}
              type="button"
              onClick={() => setRange(item)}
              className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
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

      <div ref={containerRef} className="mt-2 w-full" />
    </div>
  );
}
