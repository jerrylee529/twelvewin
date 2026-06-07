import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { buildPriceChangeMetadata } from "@/lib/seo";

export const metadata: Metadata = buildPriceChangeMetadata("week");

export default function PriceChangeFilterRedirect() {
  redirect("/technical/filter/week");
}
