import { StockLink } from "@/components/dashboard-shell";
import type { ClusterRow } from "@/lib/types";

function formatCorr(value: number) {
  return value.toFixed(2);
}

export function ClusterResultTable({
  rows,
  showChartHint = false,
}: {
  rows: ClusterRow[];
  showChartHint?: boolean;
}) {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3">
      {showChartHint ? (
        <p className="text-xs text-on-surface-variant">
          当前行业暂未生成可视化图表，以下为聚类分组结果。重新运行{" "}
          <code className="text-on-surface">python -m compute cluster_pipeline</code>{" "}
          后可查看散点图、关系图与热力图。
        </p>
      ) : null}

      <div className="terminal-pane min-h-0 flex-1 overflow-auto">
        <table className="min-w-full border-collapse text-left text-xs">
          <thead className="sticky top-0 z-10 bg-surface-container-high">
            <tr className="border-b border-on-surface/10">
              <th className="px-3 py-2 font-semibold text-on-surface-variant">序号</th>
              <th className="px-3 py-2 font-semibold text-on-surface-variant">簇心</th>
              <th className="px-3 py-2 font-semibold text-on-surface-variant">聚类成员</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.id}
                className="border-b border-on-surface/5 align-top hover:bg-surface-container-high/40"
              >
                <td className="px-3 py-3 tabular-nums text-on-surface-variant">
                  {row.id}
                </td>
                <td className="px-3 py-3 whitespace-nowrap">
                  <StockLink code={row.code} name={row.name} />
                </td>
                <td className="px-3 py-3">
                  <div className="flex flex-wrap gap-x-3 gap-y-1.5">
                    {row.items.map((item) => (
                      <span key={item.code} className="inline-flex items-center gap-1">
                        <StockLink code={item.code} name={item.name} />
                        {item.code !== row.code ? (
                          <span className="tabular-nums text-on-surface-variant">
                            ({formatCorr(item.corr)})
                          </span>
                        ) : null}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
