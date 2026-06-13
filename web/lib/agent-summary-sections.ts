export type SummarySection = {
  title: string;
  content: string;
};

const SECTION_HEADING =
  /^(?:#{1,3}\s+(.+)|\*\*(.+?)\*\*)\s*(?:（[^）]*）)?\s*$/;

/** Split agent summary markdown into titled sections (概要 / 基本面 / …). */
export function parseSummarySections(raw: string): SummarySection[] {
  const text = raw.trim();
  if (!text) {
    return [];
  }

  const sections: SummarySection[] = [];
  let current: SummarySection | null = null;

  for (const line of text.split("\n")) {
    const match = line.match(SECTION_HEADING);
    const title = match?.[1] || match?.[2];
    if (title) {
      if (current) {
        sections.push(current);
      }
      current = { title: title.trim(), content: "" };
      continue;
    }

    if (current) {
      current.content += `${line}\n`;
    } else {
      current = { title: "概要", content: `${line}\n` };
    }
  }

  if (current) {
    sections.push({
      title: current.title,
      content: current.content.trim(),
    });
  }

  return sections.filter(
    (section) => section.title.length > 0 && section.content.length > 0,
  );
}
