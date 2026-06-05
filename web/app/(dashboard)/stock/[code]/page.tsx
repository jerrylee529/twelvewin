import { Suspense } from "react";
import { StockAgentPanel } from "@/components/stock-agent-panel";
import { StockLiveQuote } from "@/components/stock-live-quote";
import { StockChartSection } from "@/components/stock-chart-section";
import { StockFinanceSection } from "@/components/stock-finance-section";
import { StockQuoteProvider } from "@/components/stock-quote-provider";
import {
  StockChartSkeleton,
  StockFinanceSkeleton,
  StockStatsSkeleton,
} from "@/components/stock-skeletons";

function ChartSuspenseFallback() {
  return (
    <>
      <StockChartSkeleton />
      <StockStatsSkeleton />
    </>
  );
}

export default async function StockPage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  const { code } = await params;

  return (
    <StockQuoteProvider code={code}>
      <div className="w-full max-w-[var(--container-max-width)] pb-10">
        <div className="flex flex-col gap-6 xl:gap-8 lg:flex-row lg:items-start">
          <div className="min-w-0 flex-1">
            <StockLiveQuote code={code} />

            <Suspense fallback={<ChartSuspenseFallback />}>
              <StockChartSection code={code} />
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
