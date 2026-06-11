"use client";

import type { ReactNode } from "react";
import {
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type Header,
  type SortingState,
} from "@tanstack/react-table";
import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown } from "lucide-react";
import { StockLink } from "@/components/dashboard-shell";
import { Chip } from "@/components/ui/primitives";
import { formatStockCode } from "@/lib/navigation";
import {
  buildRankingColumnDefs,
  exportRankingCsv,
  formatMarketCapCell,
  formatRankingValue,
  formatSignedPercent,
  isUndervalued,
  MARKET_CAP_KEYS,
  parseRankingNumber,
  SIGNED_PERCENT_KEYS,
  signedToneClass,
  type RankingRow,
} from "@/lib/ranking-columns";

export function SortableHeader({
  header,
}: {
  header: Header<RankingRow, unknown>;
}) {
  if (header.isPlaceholder) {
    return null;
  }

  const sorted = header.column.getIsSorted();

  return (
    <button
      type="button"
      onClick={header.column.getToggleSortingHandler()}
      className="inline-flex cursor-pointer items-center gap-1 whitespace-nowrap transition hover:text-on-surface"
    >
      {flexRender(header.column.columnDef.header, header.getContext())}
      {sorted === "asc" ? (
        <ChevronUp className="h-3 w-3 shrink-0 text-primary-container" />
      ) : sorted === "desc" ? (
        <ChevronDown className="h-3 w-3 shrink-0 text-primary-container" />
      ) : (
        <ChevronsUpDown className="h-3 w-3 shrink-0 opacity-30" />
      )}
    </button>
  );
}

export function ariaSortValue(
  sorted: false | "asc" | "desc",
): "ascending" | "descending" | "none" {
  return sorted === "asc"
    ? "ascending"
    : sorted === "desc"
      ? "descending"
      : "none";
}

function renderDefaultCell(key: string, row: RankingRow, value: unknown) {
  if (key === "valueprice") {
    return (
      <span className="tabular-nums">{formatRankingValue(value)}</span>
    );
  }

  if (key === "is_st") {
    return value ? <Chip tone="bearish">ST</Chip> : <span>否</span>;
  }

  if (SIGNED_PERCENT_KEYS.has(key)) {
    return (
      <span className={`tabular-nums font-medium ${signedToneClass(value)}`}>
        {formatSignedPercent(value)}
      </span>
    );
  }

  if (MARKET_CAP_KEYS.has(key)) {
    return <span className="tabular-nums">{formatMarketCapCell(value)}</span>;
  }

  if (key === "roe" || key.startsWith("roe_y") || key === "dividend_yield") {
    const numeric = parseRankingNumber(value);
    const suffix = numeric != null ? "%" : "";
    return (
      <span className="tabular-nums font-medium text-bullish">
        {formatRankingValue(value)}
        {suffix}
      </span>
    );
  }

  if (key === "pb" || key === "pb_lf") {
    return (
      <span className="tabular-nums font-medium text-bearish">
        {formatRankingValue(value)}
      </span>
    );
  }

  if (key === "close") {
    const numeric = parseRankingNumber(value);
    const tone =
      numeric != null && numeric >= 100 ? "text-bullish" : "text-bearish";
    return (
      <span className={`tabular-nums font-medium ${tone}`}>
        {formatRankingValue(value)}
      </span>
    );
  }

  return <span className="tabular-nums">{formatRankingValue(value)}</span>;
}

export function FundamentalsTable({
  rows,
  updateTime,
  total,
  pageSize = 16,
}: {
  rows: RankingRow[];
  updateTime?: string | null;
  total?: number;
  pageSize?: number;
}) {
  const columns = useMemo(
    () =>
      buildRankingColumnDefs(rows, {
        code: (value) => (
          <span className="font-medium tabular-nums text-on-surface">
            {formatStockCode(String(value))}
          </span>
        ),
        name: (row, value) => (
          <span className="inline-flex items-center gap-1.5">
            <StockLink
              code={String(row.code)}
              name={typeof value === "string" ? value : undefined}
            />
            {isUndervalued(row) ? <Chip tone="ai">低估</Chip> : null}
          </span>
        ),
        default: renderDefaultCell,
      }),
    [rows],
  );

  const [sorting, setSorting] = useState<SortingState>([]);

  const table = useReactTable({
    data: rows,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize } },
  });

  const recordTotal = total ?? rows.length;
  const pageIndex = table.getState().pagination.pageIndex;
  const currentPageSize = table.getState().pagination.pageSize;
  const rangeStart =
    recordTotal === 0 ? 0 : pageIndex * currentPageSize + 1;
  const rangeEnd = Math.min((pageIndex + 1) * currentPageSize, rows.length);
  const pageCount = table.getPageCount();

  const pageNumbers = useMemo(() => {
    const totalPages = pageCount;
    const current = pageIndex;
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, index) => index);
    }
    const pages = new Set<number>([0, totalPages - 1, current]);
    if (current > 0) pages.add(current - 1);
    if (current < totalPages - 1) pages.add(current + 1);
    if (current > 1) pages.add(current - 2);
    if (current < totalPages - 2) pages.add(current + 2);
    return Array.from(pages).sort((a, b) => a - b);
  }, [pageCount, pageIndex]);

  return (
    <div className="space-y-0">
      <div className="overflow-hidden rounded-md border border-on-surface/5 bg-surface-container">
        <div className="max-h-[72vh] overflow-auto">
          <table className="terminal-table min-w-full text-xs">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr
                  key={headerGroup.id}
                  className="border-b border-on-surface/5 bg-surface-container-lowest"
                >
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      aria-sort={ariaSortValue(header.column.getIsSorted())}
                      className="whitespace-nowrap px-3 py-3 text-left text-[11px] font-medium text-on-surface-variant"
                    >
                      <SortableHeader header={header} />
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td
                    colSpan={columns.length}
                    className="px-3 py-16 text-center text-on-surface-variant"
                  >
                    没有相关的匹配结果
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b border-on-surface/5 transition hover:bg-surface-container-high/80"
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="whitespace-nowrap px-3 py-2.5 text-on-surface"
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext(),
                        )}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex flex-col gap-3 border-t border-on-surface/5 pt-3 text-xs text-on-surface-variant sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <p className="tabular-nums text-on-surface">
            显示 {rangeStart} - {rangeEnd} / 共 {recordTotal} 条记录
          </p>
          {updateTime ? (
            <p className="label-sm tabular-nums">数据日期: {updateTime}</p>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-1">
          <PaginationButton
            disabled={!table.getCanPreviousPage()}
            onClick={() => table.setPageIndex(0)}
          >
            «
          </PaginationButton>
          <PaginationButton
            disabled={!table.getCanPreviousPage()}
            onClick={() => table.previousPage()}
          >
            上一页
          </PaginationButton>

          {pageNumbers.map((page, index) => {
            const prev = pageNumbers[index - 1];
            const showEllipsis = prev != null && page - prev > 1;
            return (
              <span key={page} className="flex items-center gap-1">
                {showEllipsis ? <span className="px-1">…</span> : null}
                <PaginationButton
                  active={page === pageIndex}
                  onClick={() => table.setPageIndex(page)}
                >
                  {page + 1}
                </PaginationButton>
              </span>
            );
          })}

          <PaginationButton
            disabled={!table.getCanNextPage()}
            onClick={() => table.nextPage()}
          >
            下一页
          </PaginationButton>
          <PaginationButton
            disabled={!table.getCanNextPage()}
            onClick={() => table.setPageIndex(pageCount - 1)}
          >
            »
          </PaginationButton>
        </div>
      </div>
    </div>
  );
}

export function exportCsv(rows: RankingRow[], metric?: string) {
  exportRankingCsv(rows, metric ? `fundamentals-${metric}.csv` : "fundamentals.csv");
}

function PaginationButton({
  children,
  disabled,
  active,
  onClick,
}: {
  children: ReactNode;
  disabled?: boolean;
  active?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`min-w-8 rounded-md px-2 py-1.5 tabular-nums transition disabled:opacity-30 ${
        active
          ? "bg-primary-container/20 text-primary-container"
          : "bg-surface-container-highest text-on-surface hover:bg-surface-container-high"
      }`}
    >
      {children}
    </button>
  );
}
