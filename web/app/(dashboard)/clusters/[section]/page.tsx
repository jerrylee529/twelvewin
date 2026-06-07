import { notFound } from "next/navigation";
import { JsonLd } from "@/components/json-ld";
import { EmptyState, PageHeader } from "@/components/dashboard-shell";
import { absoluteUrl } from "@/lib/seo";
import { ClusterChartView } from "@/components/cluster-chart-view";
import { ClusterSectionTabs } from "@/components/cluster-section-tabs";
import { Chip } from "@/components/ui/primitives";
import { getCluster, getClusterChart } from "@/lib/api";
import { getClusterTitle } from "@/lib/navigation";

const INDEX_SECTIONS = new Set(["sz50", "hs300", "zz500"]);

export default async function ClusterPage({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section } = await params;

  if (section === "all") {
    notFound();
  }

  const title = getClusterTitle(section);
  const description = INDEX_SECTIONS.has(section)
    ? "指数成分股高维聚类可视化"
    : "行业成分股高维聚类可视化";

  let data;
  let chart;
  try {
    [data, chart] = await Promise.all([
      getCluster(section),
      getClusterChart(section),
    ]);
  } catch {
    notFound();
  }

  const hasChart =
    !chart.error &&
    chart.nodes.length > 0 &&
    chart.clusters.length > 0;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: title,
    description,
    url: absoluteUrl(`/clusters/${encodeURIComponent(section)}`),
    numberOfItems: data.total,
  };

  return (
    <div className="flex h-[calc(100dvh-5.5rem)] flex-col lg:h-[calc(100dvh-6rem)]">
      <JsonLd data={jsonLd} />
      <PageHeader
        title={title}
        description={description}
        badge={<Chip tone="ai">聚类分析</Chip>}
      />

      <ClusterSectionTabs />

      {data.rows.length === 0 ? (
        <EmptyState
          message="暂无聚类数据"
          hint="请运行 python -m compute cluster_pipeline 生成并发布聚类结果。"
        />
      ) : hasChart ? (
        <ClusterChartView payload={chart} className="min-h-0 flex-1" />
      ) : (
        <EmptyState
          message="暂无图表数据"
          hint="请重新运行 python -m compute cluster_pipeline 以生成散点图、关系图和热力图数据。"
        />
      )}
    </div>
  );
}
