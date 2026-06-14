import { NextResponse } from "next/server";

export {
  getAgentStatus,
  getDifyAgentApiKey,
  getDifyApiUrl,
  getDifyScoreApiKey,
  getDifySummaryApiKey,
  isAgentEnabled,
  isAgentScoreEnabled,
  isAgentScoreWorkflow,
  isAgentSummaryWorkflow,
  type AgentChatRequest,
  type AgentScoreRequest,
  type AgentSummaryRequest,
} from "@/lib/agent-config";

export function agentNotConfiguredResponse() {
  return NextResponse.json(
    { error: "Agent is not configured on this server." },
    { status: 503 },
  );
}
