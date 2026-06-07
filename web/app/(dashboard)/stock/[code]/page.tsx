import type { Metadata } from "next";
import { Suspense } from "react";
import { JsonLd } from "@/components/json-ld";
import { StockAgentPanel } from "@/components/stock-agent-panel";
import { StockChartSection } from "@/components/stock-chart-section";
import { StockFinanceSection } from "@/components/stock-finance-section";
import { StockLivePrice } from "@/components/stock-live-quote";
import {
  quoteToHeaderProps,
  StockPageHeader,
} from "@/components/stock-page-header";
import { StockQuoteProvider } from "@/components/stock-quote-provider";
import {
  StockChartSkeleton,
  StockFinanceSkeleton,
  StockStatsSkeleton,
} from "@/components/stock-skeletons";
import { getStockBars, getStockQuote } from "@/lib/api";
import {
  absoluteUrl,
  buildStockDescription,
  buildStockMetadata,
} from "@/lib/seo";
import {
  compute52WeekRange,
  parseNumber,
  type BarRow,
} from "@/lib/stock-format";

function ChartSuspenseFallback() {
  return (
    <>
      <StockChartSkeleton />
      <StockStatsSkeleton />
    </>
  );
}

async function loadStockSeoContext(code: string) {
  const [quotePayload, barsPayload] = await Promise.all([
    getStockQuote(code).catch(() => ({ quot: null, quot_source: null })),
    getStockBars(code, { days: 252 }).catch(() => ({
      rows: [],
      updateTime: null,
      error: null,
    })),
  ]);

  const quot = quotePayload.quot;
  const name = quot?.name || code;
  const rows = (barsPayload.rows || []) as BarRow[];
  const week52 = compute52WeekRange(rows);

  return {
    quotePayload,
    name,
    description: buildStockDescription({
      code,
      name,
      trade: parseNumber(quot?.trade) || undefined,
      pe: parseNumber(quot?.per) || undefined,
      week52Low: week52.low || undefined,
      week52High: week52.high || undefined,
    }),
    updateTime: barsPayload.updateTime || quot?.update_time || null,
  };
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ code: string }>;
}): Promise<Metadata> {
  const { code } = await params;
  const context = await loadStockSeoContext(code);
  return buildStockMetadata({
    code,
    name: context.name,
    description: context.description,
  });
}

export default async function StockPage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  const { code } = await params;
  const context = await loadStockSeoContext(code);
  const headerProps = quoteToHeaderProps(code, context.quotePayload.quot);

  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "WebPage",
        name: `${context.name}(${code}) 股票研究`,
        description: context.description,
        url: absoluteUrl(`/stock/${code}`),
      },
      {
        "@type": "Corporation",
        name: context.name,
        tickerSymbol: code,
        url: absoluteUrl(`/stock/${code}`),
      },
      {
        "@type": "FinancialProduct",
        name: `${context.name} A股`,
        category: "Equity",
        identifier: code,
      },
    ],
  };

  return (
    <StockQuoteProvider code={code} initialData={context.quotePayload}>
      <JsonLd data={jsonLd} />
      <div className="w-full max-w-[var(--container-max-width)] pb-10">
        <div className="flex flex-col gap-6 xl:gap-8 lg:flex-row lg:items-start">
          <div className="min-w-0 flex-1">
            <StockPageHeader {...headerProps} />
            <p className="mt-3 max-w-3xl text-sm leading-7 text-on-surface-variant">
              {context.description}
            </p>
            <StockLivePrice />

            <Suspense fallback={<ChartSuspenseFallback />}>
              <StockChartSection
                code={code}
                name={context.name}
                initialQuot={context.quotePayload.quot}
              />
            </Suspense>

            <Suspense fallback={<StockFinanceSkeleton />}>
              <StockFinanceSection code={code} />
            </Suspense>
          </div>

          <aside className="w-full lg:w-[480px] xl:w-[520px] lg:shrink-0">
            <div className="flex min-h-0 flex-col lg:sticky lg:top-4 lg:h-[calc(100dvh-7rem)] lg:max-h-[calc(100dvh-7rem)] lg:overflow-hidden lg:rounded-sm lg:border lg:border-outline-variant/40 lg:bg-surface-container-low/50 lg:p-4">
              <StockAgentPanel code={code} />
            </div>
          </aside>
        </div>
      </div>
    </StockQuoteProvider>
  );
}
