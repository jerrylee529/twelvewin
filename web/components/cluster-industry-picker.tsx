"use client";

import { useRouter } from "next/navigation";
import { useRef, useTransition } from "react";

export function ClusterIndustryPicker({
  industries,
}: {
  industries: Array<{ id: number; name: string }>;
}) {
  const router = useRouter();
  const selectRef = useRef<HTMLSelectElement>(null);
  const [isPending, startTransition] = useTransition();

  function navigateToIndustry(raw: string) {
    const value = raw.trim();
    if (!value) {
      return;
    }

    const href = `/clusters/${encodeURIComponent(value)}`;
    startTransition(() => {
      router.push(href);
    });
  }

  function handleChange(event: React.ChangeEvent<HTMLSelectElement>) {
    navigateToIndustry(event.target.value);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    navigateToIndustry(selectRef.current?.value ?? "");
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-lg border border-on-surface/5 bg-surface-container-low p-4 sm:flex-row sm:items-end"
    >
      <label className="flex min-w-0 flex-1 flex-col gap-1 text-xs text-on-surface-variant">
        行业
        <select
          ref={selectRef}
          name="industry"
          defaultValue=""
          onChange={handleChange}
          disabled={isPending}
          className="trading-input w-full cursor-pointer rounded-sm px-3 py-2 text-sm text-on-surface outline-none disabled:cursor-wait disabled:opacity-60"
        >
          <option value="">请选择行业</option>
          {industries.map((item) => (
            <option key={item.id} value={item.name}>
              {item.name}
            </option>
          ))}
        </select>
      </label>
      <button
        type="submit"
        disabled={isPending}
        className="btn-primary-container rounded-sm px-4 py-2 text-xs font-medium transition hover:opacity-90 disabled:cursor-wait disabled:opacity-60"
      >
        {isPending ? "加载中…" : "查看聚类"}
      </button>
    </form>
  );
}
