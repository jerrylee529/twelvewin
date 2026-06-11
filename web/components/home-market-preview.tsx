import Link from "next/link";
import { ArrowRight, Flame, Gem } from "lucide-react";
import { getRanking, getTechnical } from "@/lib/api";
import {
  formatRankingValue,
  formatStockCodeValue,
  parseRankingNumber,
  type RankingRow,
} from "@/lib/ranking-columns";

const PREVIEW_COUNT = 5;

type PreviewList = {
  title: string;
  href: string;
  icon: typeof Flame;
  valueLabel: string;
  rows: RankingRow[];
  renderValue: (row: RankingRow) => string;
  valueClassName?: string;
};

async function loadPreviewLists(): Promise<PreviewList[]> {
  const [highest, pe] = await Promise.allSettled([
    getTechnical("highest", true),
    getRanking("pe", true),
  ]);

  const lists: PreviewList[] = [];

  if (highest.status === "fulfilled" && highest.value.rows.length > 0) {
    lists.push({
      title: "创历史新高",
      href: "/technical/highest",
      icon: Flame,
      valueLabel: "股价",
      rows: highest.value.rows.slice(0, PREVIEW_COUNT),
      renderValue: (row) => formatRankingValue(row.close),
      valueClassName: "text-bullish",
    });
  }

  if (pe.status === "fulfilled" && pe.value.rows.length > 0) {
    lists.push({
      title: "低市盈率",
      href: "/fundamentals?metric=pe",
      icon: Gem,
      valueLabel: "市盈率",
      rows: pe.value.rows.slice(0, PREVIEW_COUNT),
      renderValue: (row) =>
        formatRankingValue(row.pe_ttm ?? row.per ?? row.pe),
      valueClassName: "text-primary-container",
    });
  }

  return lists;
}

function PreviewRow({
  row,
  value,
  valueClassName,
}: {
  row: RankingRow;
  value: string;
  valueClassName?: string;
}) {
  const code = formatStockCodeValue(row.code);
  const name = typeof row.name === "string" ? row.name : code;

  return (
    <Link
      href={`/stock/${code}`}
      className="flex items-center justify-between gap-3 px-4 py-2.5 transition hover:bg-surface-container-high"
    >
      <span className="flex min-w-0 items-center gap-2.5">
        <span className="label-sm w-14 shrink-0 tabular-nums">{code}</span>
        <span className="truncate text-sm text-on-surface">{name}</span>
      </span>
      <span
        className={`shrink-0 text-sm font-medium tabular-nums ${valueClassName ?? "text-on-surface"}`}
      >
        {value}
      </span>
    </Link>
  );
}

export async function HomeMarketPreview() {
  let lists: PreviewList[] = [];
  try {
    lists = await loadPreviewLists();
  } catch {
    return null;
  }

  if (lists.length === 0) {
    return null;
  }

  return (
    <section className="border-t border-on-surface/5 bg-surface py-[var(--pane-margin)]">
      <div className="mx-auto mb-6 max-w-[var(--container-max-width)] px-4 lg:px-8">
        <p className="label-zh text-primary-container">今日市场信号</p>
        <h2 className="headline-md mt-2 text-on-surface">日终榜单速览</h2>
      </div>
      <div className="mx-auto grid max-w-[var(--container-max-width)] gap-[var(--terminal-gap)] px-4 sm:grid-cols-2 lg:px-8">
        {lists.map((list) => {
          const Icon = list.icon;
          return (
            <div key={list.href} className="terminal-pane flex flex-col">
              <div className="flex items-center justify-between border-b border-on-surface/5 px-4 py-3">
                <span className="inline-flex items-center gap-2">
                  <Icon className="h-4 w-4 text-primary-container" strokeWidth={1.5} />
                  <span className="text-sm font-semibold text-on-surface">
                    {list.title}
                  </span>
                </span>
                <span className="label-sm">{list.valueLabel}</span>
              </div>
              <div className="flex-1 divide-y divide-on-surface/5">
                {list.rows.map((row) => (
                  <PreviewRow
                    key={String(row.code)}
                    row={row}
                    value={list.renderValue(row)}
                    valueClassName={list.valueClassName}
                  />
                ))}
              </div>
              <Link
                href={list.href}
                className="inline-flex items-center gap-1 border-t border-on-surface/5 px-4 py-3 text-sm text-primary-container transition hover:text-on-surface"
              >
                查看完整榜单
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          );
        })}
      </div>
    </section>
  );
}
