import type { Metadata } from "next";
import { EmptyState, PageHeader } from "@/components/dashboard-shell";
import { JsonLd } from "@/components/json-ld";
import { RankingTable } from "@/components/ranking-table";
import { Chip } from "@/components/ui/primitives";
import { getValueRanking } from "@/lib/api";
import { absoluteUrl, buildPageMetadata, VALUE_RANKING_META } from "@/lib/seo";
import type { TableResponse } from "@/lib/types";

export const metadata: Metadata = buildPageMetadata({
  title: `A股${VALUE_RANKING_META.title}`,
  description: `${VALUE_RANKING_META.description}。每日日终更新。`,
  path: "/value",
  keywords: ["A股", "内在价值", "低估股票", "价值投资"],
});

const EMPTY_RESPONSE: TableResponse = {
  total: 0,
  rows: [],
  updateTime: null,
  error: "API unavailable",
};

export default async function ValueRankingPage() {
  let data = EMPTY_RESPONSE;
  try {
    data = await getValueRanking();
  } catch {
    data = EMPTY_RESPONSE;
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: VALUE_RANKING_META.title,
    description: VALUE_RANKING_META.description,
    url: absoluteUrl("/value"),
    numberOfItems: data.total,
  };

  return (
    <>
      <JsonLd data={jsonLd} />
      <PageHeader
        title={VALUE_RANKING_META.title}
        description={VALUE_RANKING_META.description}
        updateTime={data.updateTime}
        badge={<Chip tone="gold">基本面</Chip>}
      />

      {data.error && data.rows.length === 0 ? (
        <EmptyState
          message="暂无已发布的数据"
          hint="请先在服务端运行 python -m compute ranking_pipeline 生成并发布估值排行。"
        />
      ) : (
        <RankingTable rows={data.rows} />
      )}
    </>
  );
}
