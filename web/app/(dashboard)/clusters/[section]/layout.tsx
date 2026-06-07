import type { Metadata } from "next";
import { buildClusterMetadata, buildPageMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ section: string }>;
}): Promise<Metadata> {
  const { section } = await params;
  if (section === "all") {
    return buildPageMetadata({
      title: "A股行业聚类导航",
      description: "浏览全部行业聚类分析入口，查看行业成分股相关性热力图。",
      path: "/clusters/all",
      keywords: ["A股", "行业聚类", "板块分析"],
    });
  }
  return buildClusterMetadata(section);
}

export default function ClusterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
