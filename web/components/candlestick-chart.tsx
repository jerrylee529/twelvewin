"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  type IChartApi,
  type ISeriesApi,
} from "lightweight-charts";

type BarRow = [string, number, number, number, number];

/* Keep in sync with --bullish / --bearish tokens in globals.css */
const CHART_COLORS = {
  background: "#171f33",
  text: "#8b95b8",
  grid: "#131b2e",
  up: "#f6465d",
  down: "#0ecb81",
};

export function CandlestickChart({ rows }: { rows: BarRow[] }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

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
        background: { type: ColorType.Solid, color: CHART_COLORS.background },
        textColor: CHART_COLORS.text,
        fontFamily,
        fontSize: 11,
      },
      grid: {
        vertLines: { color: CHART_COLORS.grid },
        horzLines: { color: CHART_COLORS.grid },
      },
      width: containerRef.current.clientWidth,
      height: 420,
      rightPriceScale: {
        borderVisible: false,
      },
      timeScale: {
        borderVisible: false,
      },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: CHART_COLORS.up,
      downColor: CHART_COLORS.down,
      borderUpColor: CHART_COLORS.up,
      borderDownColor: CHART_COLORS.down,
      wickUpColor: CHART_COLORS.up,
      wickDownColor: CHART_COLORS.down,
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

    seriesRef.current.setData(
      rows.map(([date, open, close, low, high]) => ({
        time: date,
        open,
        close,
        low,
        high,
      })),
    );

    chartRef.current?.timeScale().fitContent();
  }, [rows]);

  return (
    <div
      ref={containerRef}
      className="terminal-pane w-full overflow-hidden p-1"
    />
  );
}
