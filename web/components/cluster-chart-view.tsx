"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import type { EChartsOption } from "echarts";
import { Pane } from "@/components/ui/primitives";
import type { ClusterChartPayload } from "@/lib/types";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

const CLUSTER_COLORS = [
  "#4ade80",
  "#60a5fa",
  "#f472b6",
  "#fbbf24",
  "#a78bfa",
  "#fb7185",
  "#2dd4bf",
  "#38bdf8",
  "#c084fc",
  "#facc15",
  "#34d399",
  "#818cf8",
];

type ChartMode = "scatter" | "graph" | "heatmap";

function clusterColor(clusterId: number) {
  if (clusterId <= 0) {
    return "#8b9292";
  }
  return CLUSTER_COLORS[(clusterId - 1) % CLUSTER_COLORS.length];
}

function baseTextStyle() {
  return {
    color: "#c1c8c8",
    fontFamily: "var(--font-sans)",
  };
}

function tooltipItem(params: unknown) {
  return (Array.isArray(params) ? params[0] : params) as {
    data?: Record<string, unknown>;
    dataType?: string;
  };
}

function buildScatterOption(payload: ClusterChartPayload): EChartsOption {
  const seriesMap = new Map<number, ClusterChartPayload["nodes"]>();
  for (const node of payload.nodes) {
    const bucket = seriesMap.get(node.clusterId) ?? [];
    bucket.push(node);
    seriesMap.set(node.clusterId, bucket);
  }

  const series = Array.from(seriesMap.entries()).map(([clusterId, nodes]) => ({
    name: nodes[0]?.clusterName ?? `聚类 ${clusterId}`,
    type: "scatter" as const,
    symbolSize: 14,
    emphasis: { focus: "series" as const },
    itemStyle: { color: clusterColor(clusterId) },
    data: nodes.map((node) => ({
      value: [node.x, node.y],
      code: node.code,
      name: node.name,
      clusterId: node.clusterId,
      clusterName: node.clusterName,
    })),
  }));

  return {
    backgroundColor: "transparent",
    textStyle: baseTextStyle(),
    grid: { left: 48, right: 24, top: 48, bottom: 48 },
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        const item = tooltipItem(params);
        const data = item.data as {
          name?: string;
          code?: string;
          clusterName?: string;
        };
        return [
          `<strong>${data.name ?? ""}</strong>`,
          `代码：${data.code ?? ""}`,
          `簇心：${data.clusterName ?? ""}`,
        ].join("<br/>");
      },
    },
    legend: {
      type: "scroll",
      top: 0,
      textStyle: baseTextStyle(),
    },
    xAxis: {
      type: "value",
      name: "维度 1",
      axisLine: { lineStyle: { color: "#414848" } },
      splitLine: { lineStyle: { color: "#222a3e" } },
    },
    yAxis: {
      type: "value",
      name: "维度 2",
      axisLine: { lineStyle: { color: "#414848" } },
      splitLine: { lineStyle: { color: "#222a3e" } },
    },
    series,
  };
}

function buildGraphOption(payload: ClusterChartPayload): EChartsOption {
  const categories = payload.clusters.map((cluster) => ({
    name: cluster.name,
  }));

  return {
    backgroundColor: "transparent",
    textStyle: baseTextStyle(),
    tooltip: {
      formatter: (params) => {
        const item = tooltipItem(params);
        if (item.dataType === "edge") {
          const edge = item.data as { value?: number };
          return `相关度：${(edge.value ?? 0).toFixed(2)}`;
        }
        const node = item.data as { name?: string; id?: string };
        return `<strong>${node.name ?? ""}</strong><br/>代码：${node.id ?? ""}`;
      },
    },
    legend: {
      type: "scroll",
      bottom: 0,
      textStyle: baseTextStyle(),
      data: categories.map((item) => item.name),
    },
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        draggable: true,
        categories,
        label: {
          show: true,
          position: "right",
          color: "#dbe2fd",
          fontSize: 10,
        },
        force: {
          repulsion: 180,
          gravity: 0.08,
          edgeLength: [50, 140],
        },
        lineStyle: {
          color: "source",
          curveness: 0.12,
          opacity: 0.45,
        },
        data: payload.nodes.map((node) => ({
          id: node.code,
          name: node.name,
          category: Math.max(node.clusterId - 1, 0),
          symbolSize: node.clusterName === node.name ? 22 : 14,
          itemStyle: { color: clusterColor(node.clusterId) },
        })),
        links: payload.edges.map((edge) => ({
          source: edge.source,
          target: edge.target,
          value: edge.corr,
          lineStyle: {
            width: Math.max(edge.corr * 2.5, 1),
          },
        })),
      },
    ],
  };
}

function buildHeatmapOption(payload: ClusterChartPayload): EChartsOption {
  const labels = payload.heatmap.labels;
  const axisLabels = labels.map((item) => item.name);
  const heatmapData = payload.heatmap.values.flatMap((row, rowIndex) =>
    row.map((value, colIndex) => [colIndex, rowIndex, value]),
  );

  return {
    backgroundColor: "transparent",
    textStyle: baseTextStyle(),
    grid: { left: 120, right: 24, top: 24, bottom: 120 },
    tooltip: {
      position: "top",
      formatter: (params) => {
        const item = tooltipItem(params);
        const point = item.data as unknown as [number, number, number];
        const row = labels[point[1]];
        const col = labels[point[0]];
        return `${row?.name ?? ""} × ${col?.name ?? ""}<br/>相关度：${point[2].toFixed(2)}`;
      },
    },
    xAxis: {
      type: "category",
      data: axisLabels,
      splitArea: { show: true },
      axisLabel: { rotate: 90, fontSize: 10, color: "#c1c8c8" },
    },
    yAxis: {
      type: "category",
      data: axisLabels,
      splitArea: { show: true },
      axisLabel: { fontSize: 10, color: "#c1c8c8" },
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: 10,
      inRange: {
        color: ["#312e81", "#131b2e", "#4ade80"],
      },
      textStyle: baseTextStyle(),
    },
    series: [
      {
        name: "相关度",
        type: "heatmap",
        data: heatmapData,
        emphasis: {
          itemStyle: { shadowBlur: 8, shadowColor: "rgba(0,0,0,0.4)" },
        },
      },
    ],
  };
}

const MODE_META: Record<ChartMode, { label: string; hint: string }> = {
  scatter: {
    label: "散点图",
    hint: "t-SNE 降维后的二维分布，颜色代表聚类",
  },
  graph: {
    label: "关系图",
    hint: "边表示 Pearson 相关 ≥ 0.5 的股票对，线宽代表相关强度",
  },
  heatmap: {
    label: "热力图",
    hint: "按聚类排序的相关矩阵，颜色越亮正相关越强",
  },
};

export function ClusterChartView({
  payload,
  className = "",
}: {
  payload: ClusterChartPayload;
  className?: string;
}) {
  const [mode, setMode] = useState<ChartMode>("scatter");
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [chartHeight, setChartHeight] = useState(480);

  useEffect(() => {
    const container = chartContainerRef.current;
    if (!container) {
      return;
    }

    const updateHeight = () => {
      const nextHeight = Math.floor(container.getBoundingClientRect().height);
      if (nextHeight > 0) {
        setChartHeight(nextHeight);
      }
    };

    updateHeight();
    const observer = new ResizeObserver(updateHeight);
    observer.observe(container);

    return () => observer.disconnect();
  }, [mode]);

  const option = useMemo(() => {
    if (mode === "graph") {
      return buildGraphOption(payload);
    }
    if (mode === "heatmap") {
      return buildHeatmapOption(payload);
    }
    return buildScatterOption(payload);
  }, [mode, payload]);

  return (
    <div className={`flex min-h-0 flex-col gap-3 ${className}`}>
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-sm border border-outline-variant/40 p-0.5">
          {(Object.keys(MODE_META) as ChartMode[]).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => setMode(key)}
              className={`rounded-sm px-3 py-1.5 text-sm transition-colors ${
                mode === key
                  ? "bg-surface-container-high text-on-surface"
                  : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {MODE_META[key].label}
            </button>
          ))}
        </div>
        <p className="text-sm text-on-surface-variant">{MODE_META[mode].hint}</p>
      </div>

      <div ref={chartContainerRef} className="min-h-0 flex-1">
        <Pane className="h-full overflow-hidden p-2">
          <ReactECharts
            option={option}
            style={{ height: chartHeight, width: "100%" }}
            notMerge
            lazyUpdate
          />
        </Pane>
      </div>
    </div>
  );
}
