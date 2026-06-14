import { NextResponse } from "next/server";

import {
  agentNotConfiguredResponse,
  getDifyApiUrl,
  getDifyScoreApiKey,
  isAgentScoreEnabled,
  isAgentScoreWorkflow,
  type AgentScoreRequest,
} from "@/lib/agent-server";
import { extractAgentAnswer, parseAgentScoreResponse } from "@/lib/agent-score";

const SCORE_QUERY = `请对当前股票进行投资价值综合评分（0–100，越高表示综合投资价值越高）。

步骤：
1. 调用 get_research_context 获取完整研究上下文
2. 按六维框架计算各子分数及加权总分：估值吸引力(25%)、盈利质量(25%)、成长动能(20%)、股东回报(10%)、市场与技术(10%)、行业相对优势(10%)
3. 应用风险修正（ST、数据缺失、数据过期等，最多扣 15 分）
4. 先输出一个合法 JSON 代码块（schema 含 stock_code, stock_name, total_score, grade, grade_label, data_as_of, dimensions[], risk_adjustment, summary, strengths, weaknesses, data_gaps, disclaimer）
5. 再输出 Markdown 解读，章节标题使用：**综合评分**、**维度解读**、**优势与短板**、**风险提示**、**数据来源**

禁止给出买入/卖出/目标价/仓位建议。所有数字必须来自工具返回的 JSON。`;

export async function POST(request: Request) {
  if (!isAgentScoreEnabled()) {
    return agentNotConfiguredResponse();
  }

  const difyUrl = getDifyApiUrl();
  const apiKey = getDifyScoreApiKey();
  if (!difyUrl || !apiKey) {
    return agentNotConfiguredResponse();
  }

  let body: AgentScoreRequest;
  try {
    body = (await request.json()) as AgentScoreRequest;
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

  if (isAgentScoreWorkflow()) {
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

    const payload = (await difyResponse.json()) as Record<string, unknown>;
    if (!difyResponse.ok) {
      return NextResponse.json(
        { error: "Dify score workflow failed.", detail: payload },
        { status: 502 },
      );
    }

    const answer = extractAgentAnswer(payload);
    return NextResponse.json(parseAgentScoreResponse(answer));
  }

  const difyResponse = await fetch(`${difyUrl}/chat-messages`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      inputs,
      query: SCORE_QUERY,
      response_mode: "blocking",
      user: body.user || "twelvewin-web",
    }),
  });

  const payload = (await difyResponse.json()) as Record<string, unknown>;
  if (!difyResponse.ok) {
    return NextResponse.json(
      { error: "Dify score request failed.", detail: payload },
      { status: 502 },
    );
  }

  const answer = extractAgentAnswer(payload);
  return NextResponse.json(parseAgentScoreResponse(answer));
}
