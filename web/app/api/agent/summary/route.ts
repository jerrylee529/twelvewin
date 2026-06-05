import { NextResponse } from "next/server";

import {
  agentNotConfiguredResponse,
  getDifyApiUrl,
  getDifySummaryApiKey,
  isAgentEnabled,
  isAgentSummaryWorkflow,
  type AgentSummaryRequest,
} from "@/lib/agent-server";

const SUMMARY_QUERY =
  "请根据工具返回的数据，生成简洁的 A 股研究摘要：概要、基本面、技术面、风险与数据来源。禁止给出买卖建议。";

export async function POST(request: Request) {
  if (!isAgentEnabled()) {
    return agentNotConfiguredResponse();
  }

  const difyUrl = getDifyApiUrl();
  const apiKey = getDifySummaryApiKey();
  if (!difyUrl || !apiKey) {
    return agentNotConfiguredResponse();
  }

  let body: AgentSummaryRequest;
  try {
    body = (await request.json()) as AgentSummaryRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  if (!body.inputs?.stock_code?.trim()) {
    return NextResponse.json(
      { error: "inputs.stock_code is required." },
      { status: 400 },
    );
  }

  const inputs = {
    stock_code: body.inputs.stock_code.trim(),
    stock_name: body.inputs.stock_name?.trim() || body.inputs.stock_code,
    locale: body.inputs.locale || "zh-CN",
  };

  if (isAgentSummaryWorkflow()) {
    const difyResponse = await fetch(`${difyUrl}/workflows/run`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        inputs,
        response_mode: "blocking",
        user: body.user || "twelvewin-web",
      }),
    });

    const payload = await difyResponse.json();
    if (!difyResponse.ok) {
      return NextResponse.json(
        { error: "Dify workflow failed.", detail: payload },
        { status: 502 },
      );
    }

    return NextResponse.json(payload);
  }

  const difyResponse = await fetch(`${difyUrl}/chat-messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      inputs,
      query: SUMMARY_QUERY,
      response_mode: "blocking",
      user: body.user || "twelvewin-web",
    }),
  });

  const payload = await difyResponse.json();
  if (!difyResponse.ok) {
    return NextResponse.json(
      { error: "Dify summary request failed.", detail: payload },
      { status: 502 },
    );
  }

  return NextResponse.json(payload);
}
