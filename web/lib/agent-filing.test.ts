import { parseFilingAnalysisPayload } from "@/lib/agent-filing";

const SAMPLE_JSON = {
  stock_code: "000001",
  stock_name: "平安银行",
  year: 2026,
  season: 1,
  display_label: "2026 第一季度季报",
  summary:
    "2026年一季度，平安银行实现营业收入352.77亿元，同比增长4.7%；归母净利润145.23亿元，同比增长3.0%。",
  highlights: [{ title: "营收利润双增", detail: "营业收入352.77亿元", page: 3 }],
  risks: [{ level: "中", title: "净息差收窄压力", detail: "净息差1.79%", page: 18 }],
  metrics_delta: { revenue_yoy: "+4.7%" },
  management_discussion: "管理层坚持零售做强战略。",
  disclaimer: "本解读由 AI 生成，不构成投资建议。",
};

describe("parseFilingAnalysisPayload", () => {
  it("parses JSON mixed with thinking blocks and section headers", () => {
    const raw = `业绩概要
<think>我们被要求提供JSON输出，不要其他文字。</think>
详细解读
<think>
我们被要求提供JSON输出。
${JSON.stringify(SAMPLE_JSON, null, 2)}
本解读由 AI 生成，不构成投资建议。`;

    const result = parseFilingAnalysisPayload({ answer: raw });

    expect(result.error).toBeUndefined();
    expect(result.summary).toContain("352.77亿元");
    expect(result.highlights).toHaveLength(1);
    expect(result.risks).toHaveLength(1);
    expect(result.full_markdown).toContain("管理层坚持零售做强战略");
    expect(result.full_markdown).not.toContain("redacted_thinking");
    expect(result.full_markdown).not.toContain('"stock_code"');
  });

  it("prefers workflow json output over generic answer fallback", () => {
    const result = parseFilingAnalysisPayload({
      answer: "业绩概要\n<think>noise</think>",
      data: {
        outputs: {
          filing_analysis_json: JSON.stringify(SAMPLE_JSON),
          filing_analysis_markdown: "## 详细解读\n\n补充说明。",
        },
      },
    });

    expect(result.summary).toContain("352.77亿元");
    expect(result.full_markdown).toContain("补充说明");
  });
});
