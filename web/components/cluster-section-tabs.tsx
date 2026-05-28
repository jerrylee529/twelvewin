"use client";

import Link from "next/link";
import { clusterNavItems, isNavChildActive } from "@/lib/navigation";
import { usePathname } from "next/navigation";

export function ClusterSectionTabs() {
  const pathname = usePathname();

  return (
    <div className="mb-4 flex flex-wrap gap-1 border-b border-on-surface/5 pb-3">
      {clusterNavItems.map((item) => {
        const active = isNavChildActive(pathname, item);
        return (
          <Link
            key={item.key}
            href={item.href}
            className={`rounded-md px-3 py-1.5 text-xs transition ${
              active
                ? "bg-surface-bright text-on-surface shadow-[inset_0_0_0_1px_rgb(218_226_253/0.12)]"
                : "text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface"
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </div>
  );
}
