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

const JSON_FENCE = /```(?:json)?\s*([\s\S]*?)```/i;
const SECTION_HEADER = /^\s*(?:业绩概要|详细解读)\s*$/gm;
const TRAILING_DISCLAIMER =
  /\n*本解读由 AI 生成，不构成投资建议。?\s*$/g;

function stripAgentReasoning(text: string): string {
  let result = text
    .replace(/<think>[\s\S]*?(?:<\/redacted_thinking>|<\/think>)/gi, "")
    .replace(/[\s\S]*?<\/think>/gi, "")
    .replace(/<think>[\s\S]*?(?=\{)/gi, "")
    .replace(SECTION_HEADER, "")
    .replace(TRAILING_DISCLAIMER, "");

  return result.trim();
}

function stripCodeFence(text: string): string {
  const trimmed = text.trim();
  const match = trimmed.match(/^```(?:json)?\s*([\s\S]*?)```$/i);
  return match ? match[1].trim() : trimmed;
}

function extractBalancedJson(text: string): { jsonText: string; remainder: string } | null {
  const start = text.indexOf("{");
  if (start === -1) {
    return null;
  }

  let depth = 0;
  let inString = false;
  let escaped = false;

  for (let index = start; index < text.length; index += 1) {
    const char = text[index];
    if (inString) {
      if (escaped) {
        escaped = false;
      } else if (char === "\\") {
        escaped = true;
      } else if (char === '"') {
        inString = false;
      }
      continue;
    }

    if (char === '"') {
      inString = true;
      continue;
    }
    if (char === "{") {
      depth += 1;
    } else if (char === "}") {
      depth -= 1;
      if (depth === 0) {
        const jsonText = text.slice(start, index + 1);
        const remainder = `${text.slice(0, start)}${text.slice(index + 1)}`.trim();
        return { jsonText, remainder };
      }
    }
  }

  return null;
}

function extractJsonFromAgentText(text: string): {
  jsonText: string;
  remainder: string;
} | null {
  const cleaned = stripAgentReasoning(text);
  const fenceMatch = cleaned.match(JSON_FENCE);
  if (fenceMatch) {
    return {
      jsonText: fenceMatch[1].trim(),
      remainder: cleaned.replace(fenceMatch[0], "").trim(),
    };
  }

  return extractBalancedJson(cleaned);
}

function tryParseJson(text: string): unknown {
  const direct = stripCodeFence(stripAgentReasoning(text));
  try {
    return JSON.parse(direct);
  } catch {
    // fall through
  }

  const extracted = extractJsonFromAgentText(text);
  if (!extracted) {
    return null;
  }

  try {
    return JSON.parse(extracted.jsonText);
  } catch {
    return null;
  }
}

function buildFullMarkdownFromRecord(record: Record<string, unknown>): string | null {
  const sections: string[] = [];

  if (typeof record.management_discussion === "string" && record.management_discussion.trim()) {
    sections.push(`## 管理层讨论\n\n${record.management_discussion.trim()}`);
  }

  if (Array.isArray(record.accounting_notes) && record.accounting_notes.length > 0) {
    const notes = record.accounting_notes
      .filter((item): item is string => typeof item === "string" && item.trim().length > 0)
      .map((item) => `- ${item.trim()}`);
    if (notes.length > 0) {
      sections.push(`## 会计与披露说明\n\n${notes.join("\n")}`);
    }
  }

  if (typeof record.vs_prior_period === "string" && record.vs_prior_period.trim()) {
    sections.push(`## 同比变化\n\n${record.vs_prior_period.trim()}`);
  }

  if (Array.isArray(record.data_gaps) && record.data_gaps.length > 0) {
    const gaps = record.data_gaps
      .filter((item): item is string => typeof item === "string" && item.trim().length > 0)
      .map((item) => `- ${item.trim()}`);
    if (gaps.length > 0) {
      sections.push(`## 数据缺口\n\n${gaps.join("\n")}`);
    }
  }

  return sections.length > 0 ? sections.join("\n\n") : null;
}

function parseStructuredFilingRecord(
  record: Record<string, unknown>,
  markdownFallback?: string | null,
): FilingAnalysisPayload {
  const generatedMarkdown = buildFullMarkdownFromRecord(record);

  return {
    code: typeof record.stock_code === "string" ? record.stock_code : null,
    year: typeof record.year === "number" ? record.year : null,
    season: typeof record.season === "number" ? record.season : null,
    display_label:
      typeof record.display_label === "string" ? record.display_label : null,
    summary: typeof record.summary === "string" ? record.summary : null,
    highlights: record.highlights as FilingAnalysisPayload["highlights"],
    risks: record.risks as FilingAnalysisPayload["risks"],
    metrics_delta:
      record.metrics_delta && typeof record.metrics_delta === "object"
        ? (record.metrics_delta as Record<string, unknown>)
        : null,
    full_markdown:
      typeof record.full_markdown === "string" && record.full_markdown.trim()
        ? record.full_markdown
        : generatedMarkdown || markdownFallback || null,
    disclaimer:
      typeof record.disclaimer === "string" ? record.disclaimer : null,
    created_at:
      typeof record.created_at === "string" ? record.created_at : null,
  };
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
    return parseStructuredFilingRecord(record);
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
      const payload = parseStructuredFilingRecord(
        parsedWorkflow as Record<string, unknown>,
        markdownText,
      );
      return {
        ...payload,
        full_markdown: payload.full_markdown || markdownText || null,
      };
    }

    if (markdownText) {
      return {
        full_markdown: stripAgentReasoning(markdownText),
        summary: stripAgentReasoning(markdownText).slice(0, 280),
        disclaimer: "本解读由 AI 生成，不构成投资建议。",
      };
    }
  }

  const answer =
    typeof record.answer === "string"
      ? record.answer
      : typeof record.text === "string"
        ? record.text
        : "";

  const extracted = answer ? extractJsonFromAgentText(answer) : null;
  const parsed = extracted ? tryParseJson(extracted.jsonText) : answer ? tryParseJson(answer) : null;
  if (parsed && typeof parsed === "object") {
    const payload = parseStructuredFilingRecord(
      parsed as Record<string, unknown>,
      extracted?.remainder || null,
    );
    return {
      ...payload,
      full_markdown:
        payload.full_markdown ||
        (extracted?.remainder ? stripAgentReasoning(extracted.remainder) : null),
    };
  }

  if (answer) {
    const cleaned = stripAgentReasoning(answer);
    return {
      summary: cleaned.slice(0, 280),
      full_markdown: cleaned,
      disclaimer: "本解读由 AI 生成，不构成投资建议。",
    };
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
