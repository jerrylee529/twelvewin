import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import { JsonLd } from "@/components/json-ld";
import { StockAgentAside } from "@/components/stock-agent-aside";
import { StockChartSection } from "@/components/stock-chart-section";
import { StockFinanceSection } from "@/components/stock-finance-section";
import { StockLivePrice } from "@/components/stock-live-quote";
import {
  quoteToHeaderProps,
  StockPageHeader,
} from "@/components/stock-page-header";
import { StockPageNav } from "@/components/stock-page-nav";
import { StockQuoteProvider } from "@/components/stock-quote-provider";
import { StockResearchSection } from "@/components/stock-research-section";
import { StockFinanceSkeleton } from "@/components/stock-skeletons";
import { absoluteUrl, buildStockMetadata } from "@/lib/seo";
import {
  isStockPageMissing,
  loadStockPageContext,
} from "@/lib/stock-page-context";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ code: string }>;
}): Promise<Metadata> {
  const { code } = await params;
  const context = await loadStockPageContext(code);
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
  const context = await loadStockPageContext(code);

  if (isStockPageMissing(context)) {
    notFound();
  }

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
      <div className="w-full max-w-[var(--container-max-width)] pb-16">
        <StockPageHeader {...headerProps} />
        <StockLivePrice />
        <StockPageNav />

        <div id="stock-chart">
          <StockChartSection
            code={code}
            name={context.name}
            initialQuot={context.quotePayload.quot}
            initialBars={context.barsPayload}
            researchContext={context.researchContext}
          />
        </div>

        <div id="stock-research">
          <StockResearchSection context={context.researchContext} />
        </div>

        <div id="stock-finance">
          <Suspense fallback={<StockFinanceSkeleton />}>
            <StockFinanceSection code={code} />
          </Suspense>
        </div>
      </div>

      <StockAgentAside code={code} />
    </StockQuoteProvider>
  );
}
