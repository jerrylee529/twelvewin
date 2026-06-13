"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { fetchStockQuoteClient } from "@/lib/api";
import type { QuoteResponse } from "@/lib/types";

const QUOTE_REFRESH_MS = 30_000;

type StockQuoteContextValue = {
  data: QuoteResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

const StockQuoteContext = createContext<StockQuoteContextValue | null>(null);

export function StockQuoteProvider({
  code,
  initialData = null,
  children,
}: {
  code: string;
  initialData?: QuoteResponse | null;
  children: ReactNode;
}) {
  const [data, setData] = useState<QuoteResponse | null>(initialData);
  const [loading, setLoading] = useState(!initialData?.quot);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const response = await fetchStockQuoteClient(code);
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load quote");
    } finally {
      setLoading(false);
    }
  }, [code]);

  useEffect(() => {
    setLoading(!initialData?.quot);
    setData(initialData);
    setError(null);

    const source = initialData?.quot_source;
    const shouldPoll = source === "redis";

    if (!initialData?.quot) {
      void refresh();
    }

    if (!shouldPoll) {
      return;
    }

    const timer = window.setInterval(() => {
      void refresh();
    }, QUOTE_REFRESH_MS);

    return () => window.clearInterval(timer);
  }, [code, initialData, refresh]);

  return (
    <StockQuoteContext.Provider value={{ data, loading, error, refresh }}>
      {children}
    </StockQuoteContext.Provider>
  );
}

export function useStockQuote() {
  const context = useContext(StockQuoteContext);
  if (!context) {
    throw new Error("useStockQuote must be used within StockQuoteProvider");
  }
  return context;
}
