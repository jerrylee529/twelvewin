/** Rough Chinese reading speed for blog cards (~400 chars/min). */
export function estimateReadingMinutes(text: string): number {
  const chars = text.replace(/\s+/g, "").length;
  if (chars === 0) {
    return 1;
  }
  return Math.max(1, Math.round(chars / 400));
}
