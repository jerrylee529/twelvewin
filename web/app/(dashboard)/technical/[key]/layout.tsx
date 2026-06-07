import type { Metadata } from "next";
import { buildTechnicalMetadata } from "@/lib/seo";
import { TECHNICAL_META, type TechnicalKey } from "@/lib/types";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ key: string }>;
}): Promise<Metadata> {
  const { key } = await params;
  if (!(key in TECHNICAL_META)) {
    return { title: "技术面分析" };
  }
  return buildTechnicalMetadata(key as TechnicalKey);
}

export default function TechnicalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
