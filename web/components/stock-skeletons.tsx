function Pulse({ className }: { className: string }) {
  return (
    <div
      className={`animate-pulse rounded bg-surface-container-high ${className}`}
    />
  );
}

export function StockQuoteSkeleton() {
  return (
    <header className="pt-2">
      <Pulse className="h-9 w-48" />
      <Pulse className="mt-2 h-4 w-20" />
      <Pulse className="mt-6 h-11 w-36" />
      <Pulse className="mt-3 h-5 w-28" />
    </header>
  );
}

export function StockChartSkeleton() {
  return (
    <section className="mt-6">
      <div className="rounded-lg border border-outline-variant/40 px-4 py-6">
        <div className="mb-4 flex gap-2">
          {Array.from({ length: 8 }).map((_, index) => (
            <Pulse key={index} className="h-7 w-10" />
          ))}
        </div>
        <Pulse className="h-64 w-full" />
      </div>
    </section>
  );
}

export function StockStatsSkeleton() {
  return (
    <section className="mt-10">
      <Pulse className="h-7 w-32" />
      <div className="mt-2 space-y-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div
            key={index}
            className="flex items-center justify-between border-b border-outline-variant/40 py-3"
          >
            <Pulse className="h-4 w-20" />
            <Pulse className="h-4 w-24" />
          </div>
        ))}
      </div>
    </section>
  );
}

export function StockFinanceSkeleton() {
  return (
    <section className="mt-10 border-t border-outline-variant/40 py-8">
      <Pulse className="h-7 w-24" />
      <div className="mt-6 space-y-8">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index}>
            <Pulse className="h-5 w-36" />
            <Pulse className="mt-4 h-28 w-full" />
          </div>
        ))}
      </div>
    </section>
  );
}

export function StockPageSkeleton() {
  return (
    <div className="mx-auto max-w-3xl pb-10">
      <StockQuoteSkeleton />
      <StockChartSkeleton />
      <StockStatsSkeleton />
      <StockFinanceSkeleton />
    </div>
  );
}
