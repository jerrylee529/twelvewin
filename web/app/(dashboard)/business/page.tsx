import { EmptyState, PageHeader } from "@/components/dashboard-shell";
import { RankingTable } from "@/components/ranking-table";
import { Chip } from "@/components/ui/primitives";
import { getBusiness } from "@/lib/api";

export default async function BusinessPage() {
  const data = await getBusiness();

  return (
    <>
      <PageHeader
        title="行业分析"
        description="按行业维度查看业务价值与标签筛选结果"
        updateTime={data.updateTime}
        badge={<Chip tone="gold">行业</Chip>}
      />

      {data.error && data.rows.length === 0 ? (
        <EmptyState message="暂无行业分析数据" />
      ) : (
        <RankingTable rows={data.rows} />
      )}
    </>
  );
}
