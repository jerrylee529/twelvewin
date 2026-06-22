import { getResearchApiHeaders } from "@/lib/research-api-headers";
import type { AgentScoreResponse } from "@/lib/agent-score";
import type { FilingAnalysisPayload } from "@/lib/agent-filing";

export function getResearchApiBase(): string {
  return (process.env.API_URL || "http://127.0.0.1:8090").replace(/\/$/, "");
}

export async function fetchCachedFilingAnalysis(
  code: string,
  year: number,
  season: number,
): Promise<FilingAnalysisPayload | null> {
  const base = getResearchApiBase();
  const response = await fetch(
    `${base}/api/v1/stocks/${encodeURIComponent(code)}/filings/${year}/${season}/analysis`,
    {
      headers: {
        Accept: "application/json",
        ...getResearchApiHeaders(),
      },
      cache: "no-store",
    },
  );

  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    return null;
  }

  return (await response.json()) as FilingAnalysisPayload;
}

export async function fetchCachedStockScore(
  code: string,
  dataAsOf: string,
): Promise<AgentScoreResponse | null> {
  const base = getResearchApiBase();
  const params = new URLSearchParams({ data_as_of: dataAsOf });
  const response = await fetch(
    `${base}/api/v1/stocks/${encodeURIComponent(code)}/score?${params.toString()}`,
    {
      headers: {
        Accept: "application/json",
        ...getResearchApiHeaders(),
      },
      cache: "no-store",
    },
  );

  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    return null;
  }

  const payload = (await response.json()) as {
    score?: AgentScoreResponse["score"];
    markdown?: string | null;
  };

  if (!payload.score) {
    return null;
  }

  return {
    score: payload.score,
    markdown: payload.markdown || "",
  };
}

export async function saveStockScore(
  code: string,
  dataAsOf: string,
  result: AgentScoreResponse,
): Promise<void> {
  const base = getResearchApiBase();
  const params = new URLSearchParams({ data_as_of: dataAsOf });
  const response = await fetch(
    `${base}/api/v1/stocks/${encodeURIComponent(code)}/score?${params.toString()}`,
    {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...getResearchApiHeaders(),
      },
      body: JSON.stringify({
        model: "dify-workflow",
        status: "done",
        score: result.score,
        markdown: result.markdown,
      }),
    },
  );

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Failed to cache stock score: ${detail}`);
  }
}

export async function fetchResearchDataAsOf(code: string): Promise<string | null> {
  const base = getResearchApiBase();
  const response = await fetch(
    `${base}/api/v1/stocks/${encodeURIComponent(code)}/research-context`,
    {
      headers: {
        Accept: "application/json",
        ...getResearchApiHeaders(),
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    return null;
  }

  const payload = (await response.json()) as { data_as_of?: string | null };
  return payload.data_as_of?.trim() || null;
}
