"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import type { EChartsOption } from "echarts";

import type { StockScoreDimension } from "@/lib/agent-score";
import {
  scoreHexColor,
  shortDimensionLabel,
} from "@/lib/stock-score-colors";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

const GRID_COLOR = "rgb(142 150 173 / 0.16)";
const AXIS_COLOR = "rgb(142 150 173 / 0.28)";
const LABEL_COLOR = "#c5cee8";
const SERIES_LINE = "#8ab4ff";
const SERIES_FILL_INNER = "rgb(138 180 255 / 0.22)";
const SERIES_FILL_OUTER = "rgb(59 130 246 / 0.04)";

function buildAxisNameRich(dimensions: StockScoreDimension[]) {
  const rich: Record<
    string,
    {
      color: string;
      fontSize: number;
      fontWeight?: number;
      padding?: number[];
      backgroundColor?: string;
      borderRadius?: number;
    }
  > = {};

  dimensions.forEach((dimension, index) => {
    rich[`dim${index}l`] = {
      color: LABEL_COLOR,
      fontSize: 13,
      fontWeight: 500,
    };
    rich[`dim${index}s`] = {
      color: scoreHexColor(dimension.score),
      fontSize: 13,
      fontWeight: 700,
      padding: [2, 0, 0, 4],
    };
  });

  return rich;
}

function buildRadarOption(
  dimensions: StockScoreDimension[],
  seriesName: string,
): EChartsOption {
  const indicators = dimensions.map((dimension, index) => ({
    name: `{dim${index}l|${shortDimensionLabel(dimension.label)}} {dim${index}s|${dimension.score}}`,
    max: 100,
    min: 0,
  }));

  const values = dimensions.map((dimension) => dimension.score);
  const pointColors = dimensions.map((dimension) => scoreHexColor(dimension.score));

  return {
    backgroundColor: "transparent",
    animationDuration: 800,
    animationEasing: "cubicOut",
    tooltip: {
      trigger: "item",
      backgroundColor: "rgb(23 31 51 / 0.96)",
      borderColor: "rgb(138 180 255 / 0.25)",
      borderWidth: 1,
      padding: [10, 14],
      textStyle: {
        color: "#dbe2fd",
        fontSize: 12,
        lineHeight: 20,
      },
      formatter: (params) => {
        const item = params as {
          name?: string;
          value?: number[];
        };
        if (!Array.isArray(item.value)) {
          return "";
        }

        return dimensions
          .map((dimension, index) => {
            const color = scoreHexColor(dimension.score);
            const label = shortDimensionLabel(dimension.label);
            const value = item.value?.[index] ?? "—";
            return `<span style="color:${color};font-weight:600">${label}</span> <span style="color:#dbe2fd">${value}</span>`;
          })
          .join("<br/>");
      },
    },
    radar: {
      shape: "polygon",
      center: ["50%", "50%"],
      radius: "72%",
      startAngle: 90,
      splitNumber: 4,
      axisName: {
        rich: buildAxisNameRich(dimensions),
      },
      axisNameGap: 16,
      axisLine: {
        lineStyle: {
          color: AXIS_COLOR,
          type: "dashed",
          width: 1,
        },
      },
      splitLine: {
        lineStyle: {
          color: GRID_COLOR,
          type: "dashed",
          width: 1,
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ["transparent", "rgb(138 180 255 / 0.025)"],
        },
      },
      indicator: indicators,
    },
    series: [
      {
        type: "radar",
        name: seriesName,
        symbol: "circle",
        symbolSize: 10,
        lineStyle: {
          color: SERIES_LINE,
          width: 2.5,
          shadowColor: "rgb(138 180 255 / 0.45)",
          shadowBlur: 10,
        },
        areaStyle: {
          color: {
            type: "radial",
            x: 0.5,
            y: 0.5,
            r: 0.65,
            colorStops: [
              { offset: 0, color: SERIES_FILL_INNER },
              { offset: 1, color: SERIES_FILL_OUTER },
            ],
          },
        },
        emphasis: {
          lineStyle: {
            width: 3,
          },
          areaStyle: {
            color: "rgb(138 180 255 / 0.16)",
          },
        },
        data: [
          {
            value: values,
            name: seriesName,
            itemStyle: {
              color: ((params: { dimensionIndex?: number }) =>
                pointColors[params.dimensionIndex ?? 0] ?? SERIES_LINE) as unknown as string,
              borderColor: "#dbe2fd",
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: "rgb(138 180 255 / 0.35)",
            },
          },
        ],
      },
    ],
  };
}

export function StockScoreRadar({
  dimensions,
  seriesName,
  className,
}: {
  dimensions: StockScoreDimension[];
  seriesName: string;
  className?: string;
}) {
  const option = useMemo(
    () => buildRadarOption(dimensions, seriesName),
    [dimensions, seriesName],
  );

  if (dimensions.length === 0) {
    return null;
  }

  return (
    <div className={className ?? "mx-auto w-full max-w-[480px]"}>
      <ReactECharts
        option={option}
        style={{ height: "min(420px, 72vw)", width: "100%", minHeight: 360 }}
        opts={{ renderer: "svg" }}
        notMerge
        lazyUpdate
      />
    </div>
  );
}
