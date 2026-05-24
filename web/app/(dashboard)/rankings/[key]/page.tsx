import { redirect } from "next/navigation";
import { RANKING_META } from "@/lib/types";

const VALID_KEYS = new Set<string>(Object.keys(RANKING_META));

export default async function RankingPage({
  params,
}: {
  params: Promise<{ key: string }>;
}) {
  const { key } = await params;

  if (!VALID_KEYS.has(key)) {
    redirect("/fundamentals?metric=pe");
  }

  redirect(`/fundamentals?metric=${key}`);
}
