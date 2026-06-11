"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BrandLogo } from "@/components/brand-logo";
import { StockSearch } from "@/components/stock-search";
import { getRecentStocks, type RecentStock } from "@/lib/search-history";

const quickLinks = [
  { href: "/fundamentals?metric=pe", label: "基本面" },
  { href: "/technical/highest", label: "技术面" },
  { href: "/clusters/sz50", label: "板块聚类" },
  { href: "/business", label: "行业分析" },
];

export function HomeSearchHero() {
  const router = useRouter();
  const [recentStocks, setRecentStocks] = useState<RecentStock[]>([]);

  useEffect(() => {
    setRecentStocks(getRecentStocks());
  }, []);

  function openRecentStock(stock: RecentStock) {
    router.push(`/stock/${stock.code}`);
  }

  return (
    <section className="hero-terminal-bg flex min-h-[55vh] flex-col items-center justify-start px-4 pb-16 pt-[clamp(2.5rem,10vh,5.5rem)]">
      <div className="flex w-full max-w-2xl -translate-y-4 flex-col items-center text-center sm:-translate-y-6">
        <BrandLogo className="h-12 object-contain sm:h-14" />
        <h1 className="display-sm mt-8 text-on-surface">搜索 A 股股票</h1>
        <p className="mt-3 max-w-md body-md text-on-surface-variant">
          输入股票代码或简称，快速进入个股研究页面
        </p>

        <div className="mt-10 w-full">
          <StockSearch autoFocus variant="hero" />
        </div>

        {recentStocks.length > 0 ? (
          <div className="mt-8 w-full text-left">
            <p className="label-sm text-on-surface-variant">最近访问</p>
            <div className="mt-3 flex flex-wrap justify-center gap-2">
              {recentStocks.map((stock) => (
                <button
                  key={stock.code}
                  type="button"
                  onClick={() => openRecentStock(stock)}
                  className="rounded-full border border-outline-variant/40 bg-surface-container-low px-3 py-1.5 text-xs text-on-surface transition hover:bg-surface-container-high"
                >
                  <span className="tabular-nums text-primary-container">
                    {stock.code}
                  </span>
                  <span className="ml-1.5">{stock.name}</span>
                </button>
              ))}
            </div>
          </div>
        ) : null}

        <div className="mt-10 flex flex-wrap items-center justify-center gap-2">
          {quickLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-full px-3 py-1.5 text-sm text-on-surface-variant transition hover:bg-surface-container-high hover:text-on-surface"
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
