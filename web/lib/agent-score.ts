export type StockScoreGrade = "A" | "B" | "C" | "D" | "E";

export type StockScoreDimension = {
  key: string;
  label: string;
  score: number;
  weight: number;
  weighted_score: number;
  highlights: string[];
  evidence: string[];
};

export type StockScorePayload = {
  stock_code: string;
  stock_name: string;
  total_score: number | null;
  grade: StockScoreGrade;
  grade_label: string;
  data_as_of: string | null;
  dimensions: StockScoreDimension[];
  risk_adjustment: {
    deduction: number;
    reasons: string[];
  };
  summary: string;
  strengths: string[];
  weaknesses: string[];
  data_gaps: string[];
  disclaimer: string;
};

export type AgentScoreResponse = {
  score: StockScorePayload | null;
  markdown: string;
};

const GRADE_LABELS: Record<StockScoreGrade, string> = {
  A: "优秀",
  B: "良好",
  C: "中性",
  D: "偏弱",
  E: "较差",
};

const JSON_FENCE = /```(?:json)?\s*([\s\S]*?)```/i;

export function gradeFromScore(score: number | null): StockScoreGrade {
  if (score == null || !Number.isFinite(score)) {
    return "C";
  }
  if (score >= 80) {
    return "A";
  }
  if (score >= 65) {
    return "B";
  }
  if (score >= 50) {
    return "C";
  }
  if (score >= 35) {
    return "D";
  }
  return "E";
}

export function gradeLabelFromScore(score: number | null): string {
  return GRADE_LABELS[gradeFromScore(score)];
}

export function scoreToneClass(score: number | null): string {
  if (score == null || !Number.isFinite(score)) {
    return "text-on-surface-variant";
  }
  if (score >= 80) {
    return "text-bullish";
  }
  if (score >= 50) {
    return "text-on-surface";
  }
  return "text-bearish";
}

export function extractAgentAnswer(payload: Record<string, unknown>): string {
  if (typeof payload.answer === "string") {
    return payload.answer;
  }

  const data = payload.data;
  if (data && typeof data === "object") {
    const outputs = (data as { outputs?: Record<string, unknown> }).outputs;
    if (outputs) {
      const preferredKeys = [
        "filing_analysis_json",
        "result",
        "filing_analysis_markdown",
      ];
      for (const key of preferredKeys) {
        const value = outputs[key];
        if (typeof value === "string" && value.trim()) {
          return value;
        }
      }

      for (const value of Object.values(outputs)) {
        if (typeof value === "string" && value.trim()) {
          return value;
        }
      }
    }
  }

  return "";
}

function clampScore(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return null;
  }
  return Math.max(0, Math.min(100, Math.round(value)));
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is string => typeof item === "string");
}

function normalizeGrade(value: unknown, totalScore: number | null): StockScoreGrade {
  if (typeof value === "string") {
    const upper = value.trim().toUpperCase();
    if (upper === "A" || upper === "B" || upper === "C" || upper === "D" || upper === "E") {
      return upper;
    }
  }
  return gradeFromScore(totalScore);
}

function normalizeDimension(raw: unknown): StockScoreDimension | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }

  const item = raw as Record<string, unknown>;
  const score = clampScore(item.score);
  const weight = typeof item.weight === "number" ? item.weight : 0;
  const weightedScore =
    typeof item.weighted_score === "number"
      ? item.weighted_score
      : score != null
        ? score * weight
        : 0;

  if (typeof item.key !== "string" || typeof item.label !== "string" || score == null) {
    return null;
  }

  return {
    key: item.key,
    label: item.label,
    score,
    weight,
    weighted_score: weightedScore,
    highlights: asStringArray(item.highlights),
    evidence: asStringArray(item.evidence),
  };
}

export function normalizeStockScorePayload(raw: unknown): StockScorePayload | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }

  const item = raw as Record<string, unknown>;
  const totalScore = clampScore(item.total_score);
  const grade = normalizeGrade(item.grade, totalScore);

  const parsedDimensions = Array.isArray(item.dimensions)
    ? item.dimensions
        .map((dimension) => normalizeDimension(dimension))
        .filter((dimension): dimension is StockScoreDimension => dimension != null)
    : [];

  if (
    typeof item.stock_code !== "string" ||
    typeof item.stock_name !== "string" ||
    parsedDimensions.length === 0
  ) {
    return null;
  }

  const risk = item.risk_adjustment;
  const riskAdjustment =
    risk && typeof risk === "object"
      ? {
          deduction:
            typeof (risk as { deduction?: unknown }).deduction === "number"
              ? (risk as { deduction: number }).deduction
              : 0,
          reasons: asStringArray((risk as { reasons?: unknown }).reasons),
        }
      : { deduction: 0, reasons: [] };

  return {
    stock_code: item.stock_code,
    stock_name: item.stock_name,
    total_score: totalScore,
    grade,
    grade_label:
      typeof item.grade_label === "string" && item.grade_label.trim()
        ? item.grade_label.trim()
        : GRADE_LABELS[grade],
    data_as_of:
      typeof item.data_as_of === "string" && item.data_as_of.trim()
        ? item.data_as_of.trim()
        : null,
    dimensions: parsedDimensions,
    risk_adjustment: riskAdjustment,
    summary: typeof item.summary === "string" ? item.summary.trim() : "",
    strengths: asStringArray(item.strengths),
    weaknesses: asStringArray(item.weaknesses),
    data_gaps: asStringArray(item.data_gaps),
    disclaimer:
      typeof item.disclaimer === "string" && item.disclaimer.trim()
        ? item.disclaimer.trim()
        : "本评分基于 Twelvewin 已发布 EOD 数据，仅供研究参考，不构成投资建议。",
  };
}

export function extractJsonBlock(raw: string): { jsonText: string; markdown: string } | null {
  const match = raw.match(JSON_FENCE);
  if (!match) {
    return null;
  }

  const jsonText = match[1].trim();
  const markdown = raw.replace(match[0], "").trim();
  return { jsonText, markdown };
}

export function parseAgentScoreResponse(raw: string): AgentScoreResponse {
  const text = raw.trim();
  if (!text) {
    return { score: null, markdown: "" };
  }

  const block = extractJsonBlock(text);
  if (!block) {
    return { score: null, markdown: text };
  }

  try {
    const parsed = JSON.parse(block.jsonText) as unknown;
    return {
      score: normalizeStockScorePayload(parsed),
      markdown: block.markdown,
    };
  } catch {
    return { score: null, markdown: text };
  }
}
