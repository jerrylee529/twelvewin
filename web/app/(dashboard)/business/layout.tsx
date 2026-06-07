import type { Metadata } from "next";
import { buildPageMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPageMetadata({
  title: "A股行业分析",
  description:
    "按行业维度查看业务价值与标签筛选结果，支持日终数据更新与同业对比。",
  path: "/business",
  keywords: ["A股", "行业分析", "板块研究", "价值投资"],
});

export default function BusinessLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
