import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { EmptyState, PageHeader } from "@/components/dashboard-shell";
import { JsonLd } from "@/components/json-ld";
import { RankingTable } from "@/components/ranking-table";
import { Chip } from "@/components/ui/primitives";
import { getPriceChange } from "@/lib/api";
import Link from "next/link";
import {
  absoluteUrl,
  buildPriceChangeMetadata,
  PRICE_CHANGE_PERIOD_SLUGS,
  PRICE_CHANGE_SLUGS,
  priceChangePath,
  type PriceChangePeriodSlug,
} from "@/lib/seo";

const DEFAULT_LOW = "-30";
const DEFAULT_HIGH = "0";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ period: string }>;
}): Promise<Metadata> {
  const { period } = await params;
  if (!(period in PRICE_CHANGE_PERIOD_SLUGS)) {
    notFound();
  }
  return buildPriceChangeMetadata(period as PriceChangePeriodSlug);
}

export default async function PriceChangePeriodPage({
  params,
  searchParams,
}: {
  params: Promise<{ period: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { period: periodSlug } = await params;
  if (!(periodSlug in PRICE_CHANGE_PERIOD_SLUGS)) {
    notFound();
  }

  const period = PRICE_CHANGE_PERIOD_SLUGS[periodSlug as PriceChangePeriodSlug];
  const query = await searchParams;
  const low =
    (Array.isArray(query.low) ? query.low[0] : query.low) || DEFAULT_LOW;
  const high =
    (Array.isArray(query.high) ? query.high[0] : query.high) || DEFAULT_HIGH;
  const data = await getPriceChange(period, low, high);
  const pagePath = `/technical/filter/${periodSlug}`;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: `A股${period}涨跌幅筛选`,
    description: `按${period}涨跌幅区间筛选 A 股`,
    url: absoluteUrl(pagePath),
    numberOfItems: data.total,
  };

  return (
    <>
      <JsonLd data={jsonLd} />
      <PageHeader
        title={`${period}涨跌幅分析`}
        description="按周期和涨跌幅区间筛选 A 股走势变化"
        updateTime={data.updateTime}
        badge={<Chip tone="bullish">技术面</Chip>}
      />

      <nav
        aria-label="涨跌幅周期"
        className="mb-4 inline-flex flex-wrap rounded-sm border border-outline-variant/40 p-0.5"
      >
        {PRICE_CHANGE_SLUGS.map((slug) => (
          <Link
            key={slug}
            href={priceChangePath(slug)}
            className={`rounded-sm px-3 py-1.5 text-xs font-medium transition-colors ${
              slug === periodSlug
                ? "bg-surface-bright font-semibold text-on-surface"
                : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface"
            }`}
          >
            {PRICE_CHANGE_PERIOD_SLUGS[slug]}
          </Link>
        ))}
      </nav>

      <form
        action={pagePath}
        className="mb-4 flex flex-col gap-3 rounded-lg border border-on-surface/5 bg-surface-container-low p-3 sm:flex-row sm:items-end"
      >
        <label className="flex flex-col gap-1 text-xs text-on-surface-variant">
          周期
          <select
            name="days"
            defaultValue={period}
            className="trading-input min-w-32 rounded-sm text-on-surface"
            disabled
          >
            <option value={period}>{period}</option>
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-on-surface-variant">
          最低涨跌幅(%)
          <input
            name="low"
            type="number"
            step="0.01"
            defaultValue={low}
            className="trading-input min-w-28 rounded-sm text-on-surface"
          />
        </label>
        <label className="flex flex-col gap-1 text-xs text-on-surface-variant">
          最高涨跌幅(%)
          <input
            name="high"
            type="number"
            step="0.01"
            defaultValue={high}
            className="trading-input min-w-28 rounded-sm text-on-surface"
          />
        </label>
        <button
          type="submit"
          className="btn-primary-container rounded-sm px-4 py-2 text-xs font-medium transition hover:opacity-90"
        >
          提交
        </button>
      </form>

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
