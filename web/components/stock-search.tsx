"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Search } from "lucide-react";
import { searchInstruments } from "@/lib/api";
import { addRecentStock } from "@/lib/search-history";
import { normalizeSearchCode } from "@/lib/stock-search-utils";
import { Button, TradingInput } from "@/components/ui/primitives";
import type { InstrumentsResponse } from "@/lib/types";

type Instrument = InstrumentsResponse["instruments"][number];

type StockSearchVariant = "default" | "compact" | "hero";

export function StockSearch({
  autoFocus = false,
  compact = false,
  variant,
}: {
  autoFocus?: boolean;
  compact?: boolean;
  variant?: StockSearchVariant;
}) {
  const resolvedVariant: StockSearchVariant =
    variant ?? (compact ? "compact" : "default");
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Instrument[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [noResults, setNoResults] = useState(false);

  useEffect(() => {
    if (query.trim().length < 1) {
      setResults([]);
      setLoading(false);
      setNoResults(false);
      setActiveIndex(-1);
      return;
    }

    setNoResults(false);
    setLoading(true);

    const timer = window.setTimeout(async () => {
      try {
        const response = await searchInstruments(query.trim(), 8);
        setResults(response.instruments);
        setActiveIndex(response.instruments.length > 0 ? 0 : -1);
        setOpen(true);
      } catch {
        setResults([]);
        setActiveIndex(-1);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => window.clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, []);

  function goToStock(code: string, name?: string | null) {
    addRecentStock({ code, name: name || code });
    setOpen(false);
    setQuery("");
    setResults([]);
    setActiveIndex(-1);
    setNoResults(false);
    router.push(`/stock/${code}`);
  }

  function prefetchStock(code: string) {
    router.prefetch(`/stock/${code}`);
  }

  function confirmSearch() {
    const trimmed = query.trim();
    if (!trimmed) {
      return;
    }

    if (activeIndex >= 0 && results[activeIndex]) {
      const item = results[activeIndex];
      goToStock(item.code, item.name);
      return;
    }

    if (results.length > 0) {
      goToStock(results[0].code, results[0].name);
      return;
    }

    const code = normalizeSearchCode(trimmed);
    if (code) {
      goToStock(code);
      return;
    }

    setNoResults(true);
    setOpen(true);
  }

  const placeholder =
    resolvedVariant === "hero"
      ? "输入股票代码或名称"
      : resolvedVariant === "compact"
        ? "搜索股票/代码"
        : "代码 / 简称";

  const inputClassName =
    resolvedVariant === "hero"
      ? "rounded-none border-none px-5 py-4 text-base"
      : "rounded-none border-none";

  const shellClassName =
    resolvedVariant === "hero"
      ? "overflow-hidden rounded-full bg-surface-container-lowest shadow-lg ring-1 ring-on-surface/10 focus-within:ring-2 focus-within:ring-primary-container/50"
      : "overflow-hidden rounded-md bg-surface-container-lowest";

  const showDropdown = open && (results.length > 0 || noResults || loading);
  const dropdownClassName =
    resolvedVariant === "hero"
      ? "glass-panel absolute z-20 mt-3 w-full overflow-hidden rounded-2xl shadow-xl"
      : "glass-panel absolute z-20 mt-1 w-full overflow-hidden rounded-md";

  return (
    <div
      ref={containerRef}
      className={`relative w-full ${
        resolvedVariant === "hero" ? "max-w-2xl" : resolvedVariant === "compact" ? "" : "max-w-xl"
      }`}
    >
      <div className={`flex items-center ${shellClassName}`}>
        {resolvedVariant === "hero" ? (
          <Search className="ml-5 h-5 w-5 shrink-0 text-on-surface-variant" />
        ) : null}
        <TradingInput
          autoFocus={autoFocus}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onFocus={() => {
            if (results.length > 0 || noResults) {
              setOpen(true);
            }
          }}
          placeholder={placeholder}
          className={`min-w-0 flex-1 ${inputClassName}`}
          aria-autocomplete="list"
          aria-expanded={showDropdown}
          role="combobox"
          onKeyDown={(event) => {
            if (event.key === "ArrowDown") {
              event.preventDefault();
              if (!results.length) {
                return;
              }
              setOpen(true);
              setActiveIndex((current) =>
                current < results.length - 1 ? current + 1 : 0,
              );
              return;
            }

            if (event.key === "ArrowUp") {
              event.preventDefault();
              if (!results.length) {
                return;
              }
              setOpen(true);
              setActiveIndex((current) =>
                current > 0 ? current - 1 : results.length - 1,
              );
              return;
            }

            if (event.key === "Escape") {
              setOpen(false);
              return;
            }

            if (event.key === "Enter") {
              event.preventDefault();
              confirmSearch();
            }
          }}
        />
        {loading ? (
          <Loader2
            className={`shrink-0 animate-spin text-on-surface-variant ${
              resolvedVariant === "hero" ? "mr-5 h-5 w-5" : "mr-3 h-4 w-4"
            }`}
          />
        ) : null}
        {resolvedVariant === "hero" ? (
          <Button
            variant="primary"
            className="mr-1.5 shrink-0 rounded-full px-6 py-2.5"
            onClick={confirmSearch}
          >
            搜索
          </Button>
        ) : resolvedVariant === "compact" ? null : (
          <Button
            variant="primary"
            className="shrink-0 rounded-none px-5"
            onClick={confirmSearch}
          >
            搜索
          </Button>
        )}
      </div>

      {showDropdown ? (
        <div className={dropdownClassName} role="listbox">
          {loading && results.length === 0 ? (
            <p className="px-4 py-3 text-sm text-on-surface-variant">
              正在搜索…
            </p>
          ) : null}

          {!loading && noResults ? (
            <p className="px-4 py-3 text-sm text-on-surface-variant">
              未找到匹配股票，请检查代码或名称
            </p>
          ) : null}

          {results.map((item, index) => {
            const active = index === activeIndex;
            return (
              <button
                key={item.code}
                type="button"
                role="option"
                aria-selected={active}
                onClick={() => goToStock(item.code, item.name)}
                onMouseEnter={() => {
                  setActiveIndex(index);
                  prefetchStock(item.code);
                }}
                className={`flex w-full items-center justify-between px-4 py-3 text-left transition ${
                  resolvedVariant === "hero" ? "text-sm" : "text-xs"
                } ${
                  active
                    ? "bg-surface-container-highest"
                    : "hover:bg-surface-container-highest"
                }`}
              >
                <span>
                  <span className="font-medium tabular-nums text-primary-container">
                    {item.code}
                  </span>
                  <span className="ml-2 text-on-surface">{item.name}</span>
                </span>
                {item.industry ? (
                  <span className="label-sm">{item.industry}</span>
                ) : null}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
