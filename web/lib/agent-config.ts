export function isAgentEnabled(): boolean {
  return process.env.TW_AGENT_ENABLED === "true";
}

export function getDifyApiUrl(): string | null {
  const raw = process.env.DIFY_API_URL?.trim();
  if (!raw) {
    return null;
  }
  return raw.replace(/\/$/, "");
}

export function getDifyAgentApiKey(): string | null {
  return process.env.DIFY_STOCK_AGENT_API_KEY?.trim() || null;
}

export function getDifySummaryApiKey(): string | null {
  return (
    process.env.DIFY_STOCK_SUMMARY_API_KEY?.trim() ||
    process.env.DIFY_STOCK_AGENT_API_KEY?.trim() ||
    null
  );
}

export function isAgentSummaryWorkflow(): boolean {
  return process.env.TW_AGENT_SUMMARY_MODE === "workflow";
}

export function getAgentStatus() {
  const agentFlag = isAgentEnabled();
  const difyUrl = getDifyApiUrl();
  const apiKey = getDifyAgentApiKey();
  const missing: string[] = [];

  if (!agentFlag) {
    missing.push("TW_AGENT_ENABLED=true");
  }
  if (!difyUrl) {
    missing.push("DIFY_API_URL");
  }
  if (!apiKey) {
    missing.push("DIFY_STOCK_AGENT_API_KEY");
  }

  return {
    enabled: agentFlag && Boolean(difyUrl && apiKey),
    summaryMode: isAgentSummaryWorkflow() ? "workflow" : "chat",
    missing,
  };
}

export type AgentChatRequest = {
  query: string;
  conversationId?: string;
  user?: string;
  inputs: {
    stock_code: string;
    stock_name?: string;
    locale?: string;
  };
};

export type AgentSummaryRequest = {
  user?: string;
  inputs: {
    stock_code: string;
    stock_name?: string;
    locale?: string;
  };
};
