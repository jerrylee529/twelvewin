"use client";

const SECTIONS = [
  { id: "stock-chart", label: "走势" },
  { id: "stock-stats", label: "指标" },
  { id: "stock-research", label: "研究概览" },
  { id: "stock-finance", label: "财务" },
] as const;

export function StockPageNav() {
  return (
    <nav
      aria-label="页面章节"
      className="sticky top-0 z-20 -mx-4 mb-4 border-b border-outline-variant/40 bg-surface/95 px-4 backdrop-blur-sm sm:-mx-5 sm:px-5 lg:-mx-6 lg:px-6"
    >
      <div className="flex gap-1 overflow-x-auto py-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {SECTIONS.map((section) => (
          <a
            key={section.id}
            href={`#${section.id}`}
            className="shrink-0 rounded-full px-3 py-1.5 text-xs font-semibold text-on-surface-variant transition hover:bg-surface-container-high hover:text-on-surface"
          >
            {section.label}
          </a>
        ))}
      </div>
    </nav>
  );
}
