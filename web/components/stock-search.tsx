"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { searchInstruments } from "@/lib/api";
import { Button, TradingInput } from "@/components/ui/primitives";

type Instrument = {
  id: number;
  code: string;
  name: string;
  industry?: string | null;
};

export function StockSearch({
  autoFocus = false,
  compact = false,
}: {
  autoFocus?: boolean;
  compact?: boolean;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Instrument[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (query.trim().length < 1) {
      setResults([]);
      return;
    }

    const timer = window.setTimeout(async () => {
      try {
        const response = await searchInstruments(query.trim(), 8);
        setResults(response.instruments);
        setOpen(true);
      } catch {
        setResults([]);
      }
    }, 250);

    return () => window.clearTimeout(timer);
  }, [query]);

  function goToStock(code: string) {
    setOpen(false);
    setQuery("");
    router.push(`/stock/${code}`);
  }

  function prefetchStock(code: string) {
    router.prefetch(`/stock/${code}`);
  }

  return (
    <div className={`relative w-full ${compact ? "" : "max-w-xl"}`}>
      <div className="flex overflow-hidden rounded-md bg-surface-container-lowest">
        <TradingInput
          autoFocus={autoFocus}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onFocus={() => setOpen(results.length > 0)}
          placeholder={compact ? "搜索股票/代码" : "代码 / 简称"}
          className="rounded-none border-none"
          onKeyDown={(event) => {
            if (compact && event.key === "Enter") {
              const code = query.trim().split(/\s+/)[0];
              if (code) {
                goToStock(code);
              }
            }
          }}
        />
        {compact ? null : (
          <Button
            variant="primary"
            className="shrink-0 rounded-none px-5"
            onClick={() => {
              const code = query.trim().split(/\s+/)[0];
              if (code) {
                goToStock(code);
              }
            }}
          >
            搜索
          </Button>
        )}
      </div>

      {open && results.length > 0 ? (
        <div className="glass-panel absolute z-20 mt-1 w-full overflow-hidden rounded-md">
          {results.map((item) => (
            <button
              key={item.code}
              type="button"
              onClick={() => goToStock(item.code)}
              onMouseEnter={() => prefetchStock(item.code)}
              className="flex w-full items-center justify-between px-3 py-2.5 text-left text-xs transition hover:bg-surface-container-highest"
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
          ))}
        </div>
      ) : null}
    </div>
  );
}
