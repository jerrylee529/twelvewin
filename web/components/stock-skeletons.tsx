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
    <div className="mt-10 grid gap-8 lg:grid-cols-2 lg:items-start">
      <section>
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
      <section className="border-t border-outline-variant/40 pt-8 lg:border-t-0 lg:border-l lg:pl-8 lg:pt-0">
        <Pulse className="h-7 w-28" />
        <Pulse className="mt-4 h-16 w-full" />
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index}>
              <Pulse className="h-3 w-16" />
              <Pulse className="mt-2 h-4 w-24" />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export function StockScoreSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-end gap-4 border-b border-outline-variant/30 pb-5">
        <Pulse className="h-14 w-20" />
        <div className="space-y-2 pb-1">
          <Pulse className="h-4 w-10" />
          <Pulse className="h-6 w-32" />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2 lg:items-stretch">
        <div className="flex min-h-[420px] items-center justify-center rounded-md border border-outline-variant/30 bg-surface/40 px-2 py-6 sm:px-4">
          <Pulse className="mx-auto aspect-square w-full max-w-[320px] rounded-full" />
        </div>
        <div className="rounded-md border border-outline-variant/30 bg-surface/40 p-4">
          <Pulse className="h-4 w-16" />
          <div className="mt-4 space-y-3">
            <Pulse className="h-4 w-full" />
            <Pulse className="h-4 w-full" />
            <Pulse className="h-4 w-[85%]" />
            <Pulse className="mt-4 h-4 w-12" />
            <Pulse className="h-4 w-full" />
            <Pulse className="h-4 w-2/3" />
          </div>
        </div>
      </div>

      <p className="text-sm text-on-surface-variant">
        正在分析估值、盈利、成长等维度，通常需要 10–30 秒…
      </p>
    </div>
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
