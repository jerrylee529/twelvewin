import { NextResponse } from "next/server";

import {
  agentNotConfiguredResponse,
  getDifyAgentApiKey,
  getDifyApiUrl,
  isAgentEnabled,
  type AgentChatRequest,
} from "@/lib/agent-server";

export async function POST(request: Request) {
  if (!isAgentEnabled()) {
    return agentNotConfiguredResponse();
  }

  const difyUrl = getDifyApiUrl();
  const apiKey = getDifyAgentApiKey();
  if (!difyUrl || !apiKey) {
    return agentNotConfiguredResponse();
  }

  let body: AgentChatRequest;
  try {
    body = (await request.json()) as AgentChatRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  if (!body.query?.trim()) {
    return NextResponse.json({ error: "query is required." }, { status: 400 });
  }
  if (!body.inputs?.stock_code?.trim()) {
    return NextResponse.json(
      { error: "inputs.stock_code is required." },
      { status: 400 },
    );
  }

  const difyResponse = await fetch(`${difyUrl}/chat-messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      inputs: {
        stock_code: body.inputs.stock_code.trim(),
        stock_name: body.inputs.stock_name?.trim() || body.inputs.stock_code,
        locale: body.inputs.locale || "zh-CN",
      },
      query: body.query.trim(),
      response_mode: "streaming",
      conversation_id: body.conversationId || "",
      user: body.user || "twelvewin-web",
    }),
  });

  if (!difyResponse.ok || !difyResponse.body) {
    const detail = await difyResponse.text();
    return NextResponse.json(
      { error: "Dify request failed.", detail },
      { status: 502 },
    );
  }

  return new Response(difyResponse.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
