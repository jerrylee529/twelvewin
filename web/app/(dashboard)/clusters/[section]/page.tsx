import { notFound } from "next/navigation";
import { EmptyState, PageHeader, StockLink } from "@/components/dashboard-shell";
import { Chip, Pane } from "@/components/ui/primitives";
import { getCluster } from "@/lib/api";

const TITLES: Record<string, string> = {
  sz50: "上证50",
  hs300: "沪深300",
  zz500: "中证500",
};

export default async function ClusterPage({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section } = await params;
  const title = TITLES[section] || section;

  let data;
  try {
    data = await getCluster(section);
  } catch {
    notFound();
  }

  return (
    <>
      <PageHeader
        title={title}
        description="板块聚类结果（离线预计算）"
        badge={<Chip tone="ai">聚类分析</Chip>}
      />

      {data.rows.length === 0 ? (
        <EmptyState message="暂无聚类数据" />
      ) : (
        <div className="space-y-2">
          {data.rows.map((cluster) => (
            <Pane key={cluster.id} className="p-4">
              <h2 className="headline-md text-on-surface">
                聚类 {cluster.id} ·{" "}
                <StockLink code={cluster.code} name={cluster.name} />
              </h2>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {cluster.items.map((item, index) => (
                  <span
                    key={`${cluster.id}-${item.code}-${index}`}
                    className="inline-flex items-center gap-2 rounded-sm bg-surface-container-lowest px-2 py-1 text-xs"
                  >
                    <StockLink code={item.code} name={item.name} />
                    <span className="tabular-nums text-on-surface-variant">
                      {item.corr.toFixed(2)}
                    </span>
                  </span>
                ))}
              </div>
            </Pane>
          ))}
        </div>
      )}
    </>
  );
}
