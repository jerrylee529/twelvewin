import { Suspense } from "react";
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
      <div className="mx-auto max-w-3xl pb-10">
        <StockLiveQuote code={code} />

        <Suspense fallback={<ChartSuspenseFallback />}>
          <StockChartSection code={code} />
        </Suspense>

        <Suspense fallback={<StockFinanceSkeleton />}>
          <StockFinanceSection code={code} />
        </Suspense>
      </div>
    </StockQuoteProvider>
  );
}
