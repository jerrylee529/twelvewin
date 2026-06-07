import { notFound } from "next/navigation";
import { JsonLd } from "@/components/json-ld";
import { EmptyState, PageHeader } from "@/components/dashboard-shell";
import { absoluteUrl } from "@/lib/seo";
import { RankingTable } from "@/components/ranking-table";
import { Chip } from "@/components/ui/primitives";
import { getTechnical } from "@/lib/api";
import { TECHNICAL_META, type TechnicalKey } from "@/lib/types";

const VALID_KEYS = new Set<string>(Object.keys(TECHNICAL_META));

export default async function TechnicalPage({
  params,
}: {
  params: Promise<{ key: string }>;
}) {
  const { key } = await params;

  if (!VALID_KEYS.has(key)) {
    notFound();
  }

  const technicalKey = key as TechnicalKey;
  const meta = TECHNICAL_META[technicalKey];
  const data = await getTechnical(technicalKey);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: meta.title,
    description: meta.description,
    url: absoluteUrl(`/technical/${technicalKey}`),
    numberOfItems: data.total,
  };

  return (
    <>
      <JsonLd data={jsonLd} />
      <PageHeader
        title={meta.title}
        description={meta.description}
        updateTime={data.updateTime}
        badge={<Chip tone="bullish">技术面</Chip>}
      />

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
