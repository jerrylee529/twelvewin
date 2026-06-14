export function scoreHexColor(score: number): string {
  if (score >= 80) {
    return "#ff7a8a";
  }
  if (score >= 50) {
    return "#6ea8ff";
  }
  return "#45dfa8";
}

export function shortDimensionLabel(label: string): string {
  const map: Record<string, string> = {
    估值吸引力: "估值",
    盈利质量: "盈利",
    成长动能: "成长",
    股东回报: "股息",
    "市场与技术": "技术",
    行业相对优势: "行业",
  };
  return map[label] || label.replace(/吸引力|质量|动能|回报|相对优势/g, "").slice(0, 4);
}
