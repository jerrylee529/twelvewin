import { EmptyState, PageHeader } from "@/components/dashboard-shell";
import { ClusterIndustryPicker } from "@/components/cluster-industry-picker";
import { ClusterSectionTabs } from "@/components/cluster-section-tabs";
import { Chip } from "@/components/ui/primitives";
import { getIndustries } from "@/lib/api";

export default async function ClusterAllPage() {
  let industries: Array<{ id: number; name: string }> = [];

  try {
    const data = await getIndustries();
    industries = data.industries ?? [];
  } catch {
    industries = [];
  }

  return (
    <>
      <PageHeader
        title="全部股票"
        description="按行业查看离线预计算的聚类结果"
        badge={<Chip tone="ai">聚类分析</Chip>}
      />

      <ClusterSectionTabs />

      {industries.length === 0 ? (
        <EmptyState
          message="暂无行业列表"
          hint="请先运行 python -m compute cluster_pipeline 生成行业聚类数据。"
        />
      ) : (
        <ClusterIndustryPicker industries={industries} />
      )}
    </>
  );
}
