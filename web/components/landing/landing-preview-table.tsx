import { Chip } from "@/components/ui/primitives";

const previewRows = [
  {
    code: "600519.SH",
    name: "贵州茅台",
    ytd: 12.4,
    pe: 28.5,
    pb: 8.2,
    roe: 32.1,
  },
  {
    code: "300750.SZ",
    name: "宁德时代",
    ytd: -5.2,
    pe: 22.1,
    pb: 4.5,
    roe: 18.4,
  },
  {
    code: "601318.SH",
    name: "中国平安",
    ytd: 8.7,
    pe: 9.8,
    pb: 1.1,
    roe: 14.2,
  },
  {
    code: "000858.SZ",
    name: "五粮液",
    ytd: -2.1,
    pe: 18.2,
    pb: 4.8,
    roe: 22.5,
  },
  {
    code: "688981.SH",
    name: "中芯国际",
    ytd: 15.6,
    pe: 45.2,
    pb: 2.8,
    roe: 5.4,
  },
];

function SentimentValue({ value }: { value: number }) {
  const formatted = value > 0 ? `+${value.toFixed(1)}%` : `${value.toFixed(1)}%`;
  const className =
    value > 0 ? "text-bullish" : value < 0 ? "text-bearish" : "text-on-surface-variant";
  return <span className={`data-num ${className}`}>{formatted}</span>;
}

export function LandingPreviewTable() {
  return (
    <section className="bg-surface-container-low py-[var(--pane-margin)]">
      <div className="mx-auto max-w-[var(--container-max-width)] px-4 lg:px-8">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="label-zh">专业级量化研究环境</p>
            <h2 className="headline-md mt-1 text-on-surface">日终数据终端预览</h2>
          </div>
          <div className="flex flex-wrap gap-1">
            <Chip tone="neutral">A 股</Chip>
            <Chip tone="ai">量化</Chip>
            <Chip tone="gold">AI 估值</Chip>
          </div>
        </div>

        <div className="terminal-pane overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-surface-container-low">
                  {["代码", "公司", "年初至今", "市盈率", "市净率", "ROE"].map(
                    (col) => (
                      <th
                        key={col}
                        className="px-[var(--cell-padding-x)] py-[var(--cell-padding-y)] text-left label-zh"
                      >
                        {col}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row, index) => (
                  <tr
                    key={row.code}
                    className={
                      index % 2 === 0
                        ? "bg-surface-container"
                        : "bg-surface-container-low"
                    }
                  >
                    <td className="px-[var(--cell-padding-x)] py-[var(--cell-padding-y)] data-num text-secondary">
                      {row.code}
                    </td>
                    <td className="px-[var(--cell-padding-x)] py-[var(--cell-padding-y)] body-sm text-on-surface">
                      {row.name}
                    </td>
                    <td className="px-[var(--cell-padding-x)] py-[var(--cell-padding-y)]">
                      <SentimentValue value={row.ytd} />
                    </td>
                    <td className="px-[var(--cell-padding-x)] py-[var(--cell-padding-y)] data-num text-on-surface">
                      {row.pe.toFixed(1)}
                    </td>
                    <td className="px-[var(--cell-padding-x)] py-[var(--cell-padding-y)] data-num text-on-surface">
                      {row.pb.toFixed(1)}
                    </td>
                    <td className="px-[var(--cell-padding-x)] py-[var(--cell-padding-y)] data-num text-on-surface">
                      {row.roe.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}
