"use client";

import { Bot, X } from "lucide-react";
import { useEffect, useState } from "react";
import { StockAgentPanel } from "@/components/stock-agent-panel";

export function StockAgentDrawer({ code }: { code: string }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) {
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  return (
    <>
      <button
        type="button"
        aria-label="打开研究助手"
        className="fixed bottom-5 right-5 z-30 flex items-center gap-2 rounded-full border border-outline-variant/50 bg-surface-container-high px-4 py-2.5 text-sm font-semibold text-on-surface shadow-lg transition hover:border-outline hover:bg-surface-container-highest"
        onClick={() => setOpen(true)}
      >
        <Bot className="h-4 w-4 text-primary-container" />
        研究助手
      </button>

      {open ? (
        <div className="fixed inset-0 z-50">
          <button
            type="button"
            aria-label="关闭研究助手"
            className="absolute inset-0 bg-black/50"
            onClick={() => setOpen(false)}
          />
          <aside className="absolute right-0 top-0 flex h-full w-full max-w-md flex-col border-l border-outline-variant/40 bg-surface-container-low shadow-2xl">
            <div className="flex shrink-0 items-center justify-between border-b border-outline-variant/40 px-4 py-3">
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-on-surface-variant">
                  AI Research
                </p>
                <p className="text-sm font-semibold text-on-surface">
                  {code} 研究助手
                </p>
              </div>
              <button
                type="button"
                aria-label="关闭"
                className="rounded-md p-1.5 text-on-surface-variant transition hover:bg-surface-container-highest hover:text-on-surface"
                onClick={() => setOpen(false)}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-hidden px-4 pb-4 pt-3">
              <StockAgentPanel code={code} layout="drawer" />
            </div>
          </aside>
        </div>
      ) : null}
    </>
  );
}
