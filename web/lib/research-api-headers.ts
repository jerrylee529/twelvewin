/** Server-side headers for Twelvewin Research API key auth. */
export function getResearchApiHeaders(): HeadersInit {
  const key = process.env.TW_RESEARCH_API_KEY?.trim();
  if (!key) {
    return {};
  }
  return { "X-Twelvewin-Api-Key": key };
}
