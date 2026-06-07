import type { Metadata } from "next";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "A股行业聚类导航",
  description: "浏览全部行业聚类分析入口，查看行业成分股相关性热力图。",
  path: "/clusters/all",
  keywords: ["A股", "行业聚类", "板块分析"],
});

export default function ClusterAllLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
