/** Filing analysis response parsing for the web BFF. */

export type FilingHighlight = {
  title?: string;
  detail?: string;
  page?: number | null;
};

export type FilingRisk = {
  level?: string;
  title?: string;
  detail?: string;
  page?: number | null;
};

export type FilingAnalysisPayload = {
  code?: string | null;
  year?: number | null;
  season?: number | null;
  display_label?: string | null;
  summary?: string | null;
  highlights?: FilingHighlight[] | string[] | null;
  risks?: FilingRisk[] | string[] | null;
  metrics_delta?: Record<string, unknown> | null;
  full_markdown?: string | null;
  disclaimer?: string | null;
  created_at?: string | null;
  error?: string | null;
};

export type FilingListRow = {
  id: number;
  code: string;
  year: number;
  season: number;
  report_kind: string;
  report_type_label: string;
  display_label: string;
  filename: string;
  publish_date?: string | null;
  page_count?: number | null;
  analysis_status: string;
};

function stripCodeFence(text: string): string {
  const trimmed = text.trim();
  const match = trimmed.match(/^```(?:json)?\s*([\s\S]*?)```$/i);
  return match ? match[1].trim() : trimmed;
}

function tryParseJson(text: string): unknown {
  try {
    return JSON.parse(stripCodeFence(text));
  } catch {
    return null;
  }
}

function normalizeStringList(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((item) => {
      if (typeof item === "string") {
        return item;
      }
      if (item && typeof item === "object" && "detail" in item) {
        const detail = (item as { detail?: string }).detail;
        const title = (item as { title?: string }).title;
        return [title, detail].filter(Boolean).join("：");
      }
      return "";
    })
    .filter(Boolean);
}

export function parseFilingAnalysisPayload(raw: unknown): FilingAnalysisPayload {
  if (!raw || typeof raw !== "object") {
    return { error: "Invalid filing analysis payload." };
  }

  const record = raw as Record<string, unknown>;

  if (typeof record.summary === "string" && record.highlights !== undefined) {
    return {
      code: typeof record.code === "string" ? record.code : null,
      year: typeof record.year === "number" ? record.year : null,
      season: typeof record.season === "number" ? record.season : null,
      display_label:
        typeof record.display_label === "string" ? record.display_label : null,
      summary: record.summary,
      highlights: record.highlights as FilingAnalysisPayload["highlights"],
      risks: record.risks as FilingAnalysisPayload["risks"],
      metrics_delta:
        record.metrics_delta && typeof record.metrics_delta === "object"
          ? (record.metrics_delta as Record<string, unknown>)
          : null,
      full_markdown:
        typeof record.full_markdown === "string" ? record.full_markdown : null,
      disclaimer:
        typeof record.disclaimer === "string" ? record.disclaimer : null,
      created_at:
        typeof record.created_at === "string" ? record.created_at : null,
    };
  }

  const answer =
    typeof record.answer === "string"
      ? record.answer
      : typeof record.text === "string"
        ? record.text
        : "";

  const parsed = answer ? tryParseJson(answer) : null;
  if (parsed && typeof parsed === "object") {
    return parseFilingAnalysisPayload(parsed);
  }

  if (answer) {
    return {
      summary: answer.slice(0, 280),
      full_markdown: answer,
      disclaimer: "本解读由 AI 生成，不构成投资建议。",
    };
  }

  const workflowOutputs =
    record.data && typeof record.data === "object"
      ? (record.data as { outputs?: Record<string, unknown> }).outputs
      : undefined;

  if (workflowOutputs) {
    const jsonText =
      typeof workflowOutputs.filing_analysis_json === "string"
        ? workflowOutputs.filing_analysis_json
        : typeof workflowOutputs.result === "string"
          ? workflowOutputs.result
          : "";
    const markdownText =
      typeof workflowOutputs.filing_analysis_markdown === "string"
        ? workflowOutputs.filing_analysis_markdown
        : undefined;

    const parsedWorkflow = jsonText ? tryParseJson(jsonText) : null;
    if (parsedWorkflow && typeof parsedWorkflow === "object") {
      const payload = parseFilingAnalysisPayload(parsedWorkflow);
      return {
        ...payload,
        full_markdown: payload.full_markdown || markdownText || null,
      };
    }

    if (markdownText) {
      return {
        full_markdown: markdownText,
        summary: markdownText.slice(0, 280),
        disclaimer: "本解读由 AI 生成，不构成投资建议。",
      };
    }
  }

  return { error: "Unable to parse filing analysis response." };
}

export function filingHighlightsToStrings(
  highlights: FilingAnalysisPayload["highlights"],
): string[] {
  return normalizeStringList(highlights);
}

export function filingRisksToStrings(
  risks: FilingAnalysisPayload["risks"],
): string[] {
  return normalizeStringList(risks);
}
