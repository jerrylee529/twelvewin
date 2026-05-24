"use client";

import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useMemo, useState } from "react";
import { StockLink } from "@/components/dashboard-shell";
import { Chip } from "@/components/ui/primitives";
import {
  buildRankingColumnDefs,
  formatRankingValue,
  formatStockCodeValue,
  isUndervalued,
  type RankingRow,
} from "@/lib/ranking-columns";

export function RankingTable({
  rows,
  pageSize = 20,
}: {
  rows: RankingRow[];
  pageSize?: number;
}) {
  const [globalFilter, setGlobalFilter] = useState("");
  const columns = useMemo(
    () =>
      buildRankingColumnDefs(
        rows,
        {
          code: (value) => (
            <span className="tabular-nums">{formatStockCodeValue(value)}</span>
          ),
          name: (row, value) => (
            <span className="inline-flex items-center gap-1.5">
              <StockLink
                code={formatStockCodeValue(row.code)}
                name={typeof value === "string" ? value : undefined}
              />
              {isUndervalued(row) ? <Chip tone="ai">低估</Chip> : null}
            </span>
          ),
          default: (_key, _row, value) => (
            <span className="tabular-nums">{formatRankingValue(value)}</span>
          ),
        },
        { includeUpdateTime: true },
      ),
    [rows],
  );

  const table = useReactTable({
    data: rows,
    columns,
    state: { globalFilter },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize },
    },
  });

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <input
          value={globalFilter}
          onChange={(event) => setGlobalFilter(event.target.value)}
          placeholder="筛选代码或名称..."
          className="trading-input w-full max-w-xs rounded-sm sm:w-64"
        />
        <p className="label-sm tabular-nums">共 {rows.length} 条</p>
      </div>

      <div className="terminal-pane overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs">
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr
                  key={headerGroup.id}
                  className="bg-surface-container-lowest text-left"
                >
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      className="whitespace-nowrap px-3 py-2.5 font-medium text-on-surface-variant"
                    >
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
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
                    className="px-3 py-12 text-center text-on-surface-variant"
                  >
                    没有相关的匹配结果
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row, index) => (
                  <tr
                    key={row.id}
                    className={
                      index % 2 === 0
                        ? "bg-surface-container hover:bg-surface-container-high"
                        : "bg-surface-container-low hover:bg-surface-container-high"
                    }
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="whitespace-nowrap px-3 py-2 text-on-surface"
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

      <div className="flex items-center justify-between text-xs text-on-surface-variant">
        <span className="tabular-nums">
          {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}
        </span>
        <div className="flex gap-1">
          <button
            type="button"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="rounded-sm bg-surface-container-highest px-3 py-1.5 text-on-surface transition hover:bg-surface-container-high disabled:opacity-30"
          >
            上一页
          </button>
          <button
            type="button"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="rounded-sm bg-surface-container-highest px-3 py-1.5 text-on-surface transition hover:bg-surface-container-high disabled:opacity-30"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  );
}
