export type AgentContentSegment =
  | { type: "markdown"; content: string }
  | { type: "think"; content: string; complete: boolean };

const THINK_OPEN_TAG = "<" + "think" + ">";
const THINK_CLOSE_TAG = "<" + "/" + "think" + ">";

function thinkClosedPattern(): RegExp {
  return new RegExp(
    `${THINK_OPEN_TAG}\\s*([\\s\\S]*?)\\s*${THINK_CLOSE_TAG}`,
    "gi",
  );
}

function thinkOpenPattern(): RegExp {
  return new RegExp(`${THINK_OPEN_TAG}\\s*([\\s\\S]*)$`, "i");
}

/**
 * Split agent output into markdown segments and optional reasoning (think) blocks.
 */
export function parseAgentContent(raw: string): AgentContentSegment[] {
  const text = raw.trim();
  if (!text) {
    return [];
  }

  const segments: AgentContentSegment[] = [];
  const closedRe = thinkClosedPattern();
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = closedRe.exec(text)) !== null) {
    pushMarkdownSegment(segments, text.slice(lastIndex, match.index));
    const thinkBody = match[1].trim();
    if (thinkBody) {
      segments.push({ type: "think", content: thinkBody, complete: true });
    }
    lastIndex = match.index + match[0].length;
  }

  const tail = text.slice(lastIndex);
  const openThink = tail.match(thinkOpenPattern());
  if (openThink && openThink.index !== undefined) {
    pushMarkdownSegment(segments, tail.slice(0, openThink.index));
    const thinkBody = openThink[1].trim();
    if (thinkBody) {
      segments.push({ type: "think", content: thinkBody, complete: false });
    }
  } else {
    pushMarkdownSegment(segments, tail);
  }

  return segments;
}

function pushMarkdownSegment(
  segments: AgentContentSegment[],
  chunk: string,
) {
  const trimmed = chunk.trim();
  if (trimmed) {
    segments.push({ type: "markdown", content: trimmed });
  }
}
