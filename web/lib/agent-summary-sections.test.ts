import { parseSummarySections } from "@/lib/agent-summary-sections";

describe("parseSummarySections", () => {
  it("splits bold headings into sections", () => {
    const sections = parseSummarySections(
      "**概要**\nHello\n\n**基本面**\n- PE low",
    );
    expect(sections).toHaveLength(2);
    expect(sections[0].title).toBe("概要");
    expect(sections[1].title).toBe("基本面");
  });
});
