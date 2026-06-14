import {
  gradeFromScore,
  gradeLabelFromScore,
  normalizeStockScorePayload,
  parseAgentScoreResponse,
} from "@/lib/agent-score";

describe("parseAgentScoreResponse", () => {
  it("parses JSON block and trailing markdown", () => {
    const raw = `\`\`\`json
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "total_score": 78,
  "grade": "B",
  "grade_label": "良好",
  "data_as_of": "2026-06-10",
  "dimensions": [
    {
      "key": "valuation",
      "label": "估值吸引力",
      "score": 82,
      "weight": 0.25,
      "weighted_score": 20.5,
      "highlights": ["PE 低于行业中位数"],
      "evidence": ["fundamentals.pe_ttm"]
    }
  ],
  "risk_adjustment": { "deduction": 0, "reasons": [] },
  "summary": "综合表现良好",
  "strengths": ["盈利稳定"],
  "weaknesses": ["估值偏高"],
  "data_gaps": [],
  "disclaimer": "仅供研究参考"
}
\`\`\`

**综合评分**
表现良好。`;

    const result = parseAgentScoreResponse(raw);
    expect(result.score?.total_score).toBe(78);
    expect(result.score?.dimensions).toHaveLength(1);
    expect(result.markdown).toContain("**综合评分**");
  });

  it("returns markdown-only payload when JSON is missing", () => {
    const result = parseAgentScoreResponse("**综合评分**\n暂无数据");
    expect(result.score).toBeNull();
    expect(result.markdown).toContain("暂无数据");
  });
});

describe("normalizeStockScorePayload", () => {
  it("derives grade when missing", () => {
    const payload = normalizeStockScorePayload({
      stock_code: "000001",
      stock_name: "平安银行",
      total_score: 84,
      dimensions: [
        {
          key: "valuation",
          label: "估值吸引力",
          score: 80,
          weight: 0.25,
          weighted_score: 20,
          highlights: [],
          evidence: [],
        },
      ],
      risk_adjustment: { deduction: 0, reasons: [] },
      summary: "",
      strengths: [],
      weaknesses: [],
      data_gaps: [],
      disclaimer: "",
    });

    expect(payload?.grade).toBe("A");
    expect(payload?.grade_label).toBe("优秀");
  });
});

describe("gradeFromScore", () => {
  it("maps score bands to grades", () => {
    expect(gradeFromScore(85)).toBe("A");
    expect(gradeFromScore(70)).toBe("B");
    expect(gradeFromScore(55)).toBe("C");
    expect(gradeFromScore(40)).toBe("D");
    expect(gradeFromScore(20)).toBe("E");
    expect(gradeLabelFromScore(70)).toBe("良好");
  });
});
