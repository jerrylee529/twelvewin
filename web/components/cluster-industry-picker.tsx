"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function ClusterIndustryPicker({
  industries,
}: {
  industries: Array<{ id: number; name: string }>;
}) {
  const router = useRouter();
  const [industry, setIndustry] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = industry.trim();
    if (!value) {
      return;
    }
    router.push(`/clusters/${encodeURIComponent(value)}`);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-lg border border-on-surface/5 bg-surface-container-low p-4 sm:flex-row sm:items-end"
    >
      <label className="flex min-w-0 flex-1 flex-col gap-1 text-xs text-on-surface-variant">
        行业
        <select
          value={industry}
          onChange={(event) => setIndustry(event.target.value)}
          className="trading-input w-full rounded-sm text-on-surface"
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
        disabled={!industry}
        className="btn-primary-container rounded-sm px-4 py-2 text-xs font-medium transition hover:opacity-90 disabled:opacity-40"
      >
        查看聚类
      </button>
    </form>
  );
}
