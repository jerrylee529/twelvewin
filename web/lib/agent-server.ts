import { NextResponse } from "next/server";

export {
  getAgentStatus,
  getDifyAgentApiKey,
  getDifyApiUrl,
  getDifyFilingApiKey,
  getDifyScoreApiKey,
  getDifySummaryApiKey,
  isAgentEnabled,
  isAgentFilingEnabled,
  isAgentFilingWorkflow,
  isAgentScoreEnabled,
  isAgentScoreWorkflow,
  isAgentSummaryWorkflow,
  type AgentChatRequest,
  type AgentFilingRequest,
  type AgentScoreRequest,
  type AgentSummaryRequest,
} from "@/lib/agent-config";

export function agentNotConfiguredResponse() {
  return NextResponse.json(
    { error: "Agent is not configured on this server." },
    { status: 503 },
  );
}
