"use client";

import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronDown, Download, Filter, RefreshCw, Search } from "lucide-react";
import { useMemo, useState } from "react";
import {
  exportCsv,
  FundamentalsTable,
} from "@/components/fundamentals-table";
import { Chip, TradingInput } from "@/components/ui/primitives";
import { fundamentalMetrics } from "@/lib/navigation";
import {
  RANKING_META,
  type FundamentalScreenerQuery,
  type RankingKey,
} from "@/lib/types";

type Row = Record<string, unknown>;

const PRESET_PARAMS: Record<RankingKey, Record<string, string>> = {
  pe: { metric: "pe", pe_min: "5", pe_max: "20", sort: "pe_ttm", order: "asc" },
  pb: { metric: "pb", pb_max: "2", sort: "pb_lf", order: "asc" },
  roe: { metric: "roe", roe_min: "10", sort: "roe", order: "desc" },
  divi: {
    metric: "divi",
    dividend_yield_min: "3",
    sort: "dividend_yield",
    order: "desc",
  },
};

function buildHref(params: Record<string, string>) {
  const query = new URLSearchParams(params);
  return `/fundamentals?${query.toString()}`;
}

const FILTER_KEYS = [
  "search",
  "industry",
  "pe_min",
  "pe_max",
  "pb_max",
  "roe_min",
  "roe_3y_min",
  "dividend_yield_min",
  "float_market_cap_min",
  "float_market_cap_max",
] as const;

function summarizeActiveFilters(query: FundamentalScreenerQuery) {
  const parts: string[] = [];
  for (const key of FILTER_KEYS) {
    const value = String(query[key] ?? "").trim();
    if (value) {
      parts.push(value);
    }
  }
  if (query.exclude_st !== "false") {
    parts.push("剔除 ST");
  }
  return parts;
}

function buildQueryHref(query: FundamentalScreenerQuery, overrides: Record<string, string>) {
  const params = new URLSearchParams();
  Object.entries({ ...query, ...overrides }).forEach(([key, value]) => {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      params.set(key, String(value));
    }
  });
  return `/fundamentals?${params.toString()}`;
}

export function FundamentalsWorkspace({
  metric,
  query,
  rows,
  total,
  updateTime,
}: {
  metric: RankingKey;
  query: FundamentalScreenerQuery;
  rows: Row[];
  total: number;
  updateTime?: string | null;
}) {
  const router = useRouter();
  const [filtersExpanded, setFiltersExpanded] = useState(false);
  const meta = RANKING_META[metric];
  const activeFilterSummary = useMemo(() => summarizeActiveFilters(query), [query]);
  const currentPage = Math.max(Number(query.page ?? "1") || 1, 1);
  const pageSize = Math.max(Number(query.page_size ?? "50") || 50, 1);
  const pageCount = Math.max(Math.ceil(total / pageSize), 1);

  const industries = useMemo(() => {
    const values = new Set<string>();
    rows.forEach((row) => {
      const value = String(row.industry ?? "").trim();
      if (value) values.add(value);
    });
    return Array.from(values).sort();
  }, [rows]);

  function submitFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const params = new URLSearchParams();
    for (const [key, value] of formData.entries()) {
      const text = String(value).trim();
      if (text) {
        params.set(key, text);
      }
    }
    if (!params.has("exclude_st")) {
      params.set("exclude_st", "false");
    }
    params.set("metric", metric);
    params.set("page", "1");
    router.push(`/fundamentals?${params.toString()}`);
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <Chip tone="gold">基本面</Chip>
            <p className="title-sm">数据终端</p>
          </div>
          <h1 className="text-lg font-semibold tracking-tight text-on-surface">
            {meta.title}
          </h1>
          <p className="mt-1 text-xs text-on-surface-variant">{meta.description}</p>
          {updateTime ? (
            <p className="mt-2 label-sm tabular-nums">数据截至 {updateTime}</p>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => exportCsv(rows, metric)}
            className="inline-flex items-center gap-1.5 rounded-md border border-on-surface/10 bg-surface-container-highest px-3 py-1.5 text-xs text-on-surface transition hover:bg-surface-container-high"
          >
            <Download className="h-3.5 w-3.5" />
            导出数据
          </button>
          <button
            type="button"
            onClick={() => router.refresh()}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-on-surface/10 bg-surface-container-highest text-on-surface-variant transition hover:text-on-surface"
            aria-label="刷新"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 border-b border-on-surface/5 pb-3">
        {fundamentalMetrics.map((item) => {
          const active = item.key === metric;
          return (
            <Link
              key={item.key}
              href={buildHref(PRESET_PARAMS[item.key])}
              className={`rounded-md px-3 py-1.5 text-xs transition ${
                active
                  ? "bg-surface-bright text-on-surface shadow-[inset_0_0_0_1px_rgb(218_226_253/0.12)]"
                  : "text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface"
              }`}
            >
              {item.shortLabel}
            </Link>
          );
        })}
      </div>

      <div className="overflow-hidden rounded-md border border-on-surface/5 bg-surface-container">
        <button
          type="button"
          onClick={() => setFiltersExpanded((value) => !value)}
          aria-expanded={filtersExpanded}
          className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition hover:bg-surface-container-high"
        >
          <span className="flex min-w-0 flex-1 items-center gap-2">
            <Filter className="h-3.5 w-3.5 shrink-0 text-on-surface-variant" />
            <span className="text-xs font-medium text-on-surface">筛选条件</span>
            {!filtersExpanded && activeFilterSummary.length > 0 ? (
              <span className="truncate text-xs text-on-surface-variant">
                {activeFilterSummary.join(" · ")}
              </span>
            ) : null}
            {activeFilterSummary.length > 0 ? (
              <Chip tone="neutral">{activeFilterSummary.length}</Chip>
            ) : null}
          </span>
          <ChevronDown
            className={`h-4 w-4 shrink-0 text-on-surface-variant transition-transform ${
              filtersExpanded ? "rotate-180" : ""
            }`}
          />
        </button>

        {filtersExpanded ? (
          <form
            onSubmit={submitFilters}
            className="grid gap-3 border-t border-on-surface/5 p-4 md:grid-cols-4"
          >
        <label className="space-y-1 text-xs text-on-surface-variant">
          代码或名称
          <TradingInput name="search" defaultValue={query.search ?? ""} placeholder="600000 / 银行" />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          行业
          <select
            name="industry"
            defaultValue={query.industry ?? ""}
            className="trading-input w-full px-3 py-2 body-sm text-on-surface outline-none"
          >
            <option value="">全部行业</option>
            {industries.map((industry) => (
              <option key={industry} value={industry}>
                {industry}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          PE 最小
          <TradingInput name="pe_min" defaultValue={query.pe_min ?? ""} placeholder="5" />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          PE 最大
          <TradingInput name="pe_max" defaultValue={query.pe_max ?? ""} placeholder="20" />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          PB 最大
          <TradingInput name="pb_max" defaultValue={query.pb_max ?? ""} placeholder="2" />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          ROE 最小(%)
          <TradingInput name="roe_min" defaultValue={query.roe_min ?? ""} placeholder="10" />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          近三年 ROE 最小(%)
          <TradingInput name="roe_3y_min" defaultValue={query.roe_3y_min ?? ""} placeholder="10" />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          股息率最小(%)
          <TradingInput
            name="dividend_yield_min"
            defaultValue={query.dividend_yield_min ?? ""}
            placeholder="3"
          />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          流通市值最小(万元)
          <TradingInput
            name="float_market_cap_min"
            defaultValue={query.float_market_cap_min ?? ""}
            placeholder="500000"
          />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          流通市值最大(万元)
          <TradingInput
            name="float_market_cap_max"
            defaultValue={query.float_market_cap_max ?? ""}
            placeholder="5000000"
          />
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          排序
          <select
            name="sort"
            defaultValue={query.sort ?? PRESET_PARAMS[metric].sort}
            className="trading-input w-full px-3 py-2 body-sm text-on-surface outline-none"
          >
            <option value="pe_discount_to_industry">PE 行业折价</option>
            <option value="pb_discount_to_industry">PB 行业折价</option>
            <option value="pe_ttm">PE</option>
            <option value="pb_lf">PB</option>
            <option value="roe">ROE</option>
            <option value="dividend_yield">股息率</option>
            <option value="float_market_cap">流通市值</option>
          </select>
        </label>
        <label className="space-y-1 text-xs text-on-surface-variant">
          方向
          <select
            name="order"
            defaultValue={query.order ?? PRESET_PARAMS[metric].order}
            className="trading-input w-full px-3 py-2 body-sm text-on-surface outline-none"
          >
            <option value="asc">升序</option>
            <option value="desc">降序</option>
          </select>
        </label>
        <label className="flex items-center gap-2 text-xs text-on-surface-variant md:col-span-2">
          <input
            type="checkbox"
            name="exclude_st"
            value="true"
            defaultChecked={query.exclude_st !== "false"}
          />
          剔除 ST 股票
        </label>
        <div className="flex items-end gap-2 md:col-span-2">
          <button
            type="submit"
            className="inline-flex items-center gap-1.5 rounded-md bg-primary-container/20 px-4 py-2 text-xs font-medium text-primary-container transition hover:bg-primary-container/30"
          >
            <Search className="h-3.5 w-3.5" />
            应用筛选
          </button>
          <Link
            href={buildHref(PRESET_PARAMS[metric])}
            className="inline-flex items-center rounded-md border border-on-surface/10 px-4 py-2 text-xs text-on-surface-variant transition hover:text-on-surface"
          >
            重置当前 preset
          </Link>
        </div>
          </form>
        ) : null}
      </div>

      <FundamentalsTable
        rows={rows}
        total={total}
        updateTime={updateTime}
        pageSize={Math.max(rows.length, 1)}
      />

      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-on-surface-variant">
        <p className="tabular-nums">
          服务端分页: 第 {currentPage} / {pageCount} 页，每页 {pageSize} 条
        </p>
        <div className="flex items-center gap-2">
          <Link
            href={buildQueryHref(query, { page: String(Math.max(currentPage - 1, 1)) })}
            className={`rounded-md border border-on-surface/10 px-3 py-1.5 transition ${
              currentPage <= 1 ? "pointer-events-none opacity-40" : "hover:text-on-surface"
            }`}
          >
            上一页
          </Link>
          <Link
            href={buildQueryHref(query, { page: String(Math.min(currentPage + 1, pageCount)) })}
            className={`rounded-md border border-on-surface/10 px-3 py-1.5 transition ${
              currentPage >= pageCount ? "pointer-events-none opacity-40" : "hover:text-on-surface"
            }`}
          >
            下一页
          </Link>
        </div>
      </div>
    </div>
  );
}
