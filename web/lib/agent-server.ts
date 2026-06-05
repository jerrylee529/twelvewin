import { NextResponse } from "next/server";

export {
  getAgentStatus,
  getDifyAgentApiKey,
  getDifyApiUrl,
  getDifySummaryApiKey,
  isAgentEnabled,
  isAgentSummaryWorkflow,
  type AgentChatRequest,
  type AgentSummaryRequest,
} from "@/lib/agent-config";

export function agentNotConfiguredResponse() {
  return NextResponse.json(
    { error: "Agent is not configured on this server." },
    { status: 503 },
  );
}
