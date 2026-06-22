import { NextResponse } from "next/server";

import {
  agentNotConfiguredResponse,
  getDifyApiUrl,
  getDifyFilingApiKey,
  isAgentFilingEnabled,
  isAgentFilingWorkflow,
  type AgentFilingRequest,
} from "@/lib/agent-server";
import { parseFilingAnalysisPayload } from "@/lib/agent-filing";
import { extractAgentAnswer } from "@/lib/agent-score";
import { fetchCachedFilingAnalysis } from "@/lib/agent-research-api";
import { getResearchApiHeaders } from "@/lib/research-api-headers";

const FILING_QUERY = `请根据工具返回的财报 PDF 文本，输出结构化 JSON（字段含 summary, highlights[], risks[], metrics_delta, full_markdown, disclaimer）。
要求：
1. 数字与结论必须来自 PDF 文本，无法确认时写入 data_gaps
2. highlights/risks 条目尽量带 page 页码
3. 禁止给出买卖建议
4. 只输出一个合法 JSON 对象，不要输出思考过程、不要输出 Markdown 标题或额外说明文字
5. 若需详细解读，写入 full_markdown 字段，不要放在 JSON 外部`;

function getApiBase(): string {
  return (process.env.API_URL || "http://127.0.0.1:8090").replace(/\/$/, "");
}

async function saveFilingAnalysis(
  code: string,
  year: number,
  season: number,
  payload: ReturnType<typeof parseFilingAnalysisPayload>,
) {
  const base = getApiBase();
  const response = await fetch(
    `${base}/api/v1/stocks/${encodeURIComponent(code)}/filings/${year}/${season}/analysis`,
    {
      method: "PUT",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...getResearchApiHeaders(),
      },
      body: JSON.stringify({
        model: "dify-workflow",
        status: "done",
        summary: payload.summary,
        highlights: payload.highlights,
        risks: payload.risks,
        metrics_delta: payload.metrics_delta,
        full_markdown: payload.full_markdown,
        disclaimer:
          payload.disclaimer || "本解读由 AI 生成，不构成投资建议。",
      }),
    },
  );

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Failed to cache filing analysis: ${detail}`);
  }
}

export async function POST(request: Request) {
  if (!isAgentFilingEnabled()) {
    return agentNotConfiguredResponse();
  }

  const difyUrl = getDifyApiUrl();
  const apiKey = getDifyFilingApiKey();
  if (!difyUrl || !apiKey) {
    return agentNotConfiguredResponse();
  }

  let body: AgentFilingRequest;
  try {
    body = (await request.json()) as AgentFilingRequest;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const stockCode = body.inputs?.stock_code?.trim();
  const year = body.inputs?.year;
  const season = body.inputs?.season;
  if (!stockCode || year === undefined || season === undefined) {
    return NextResponse.json(
      { error: "inputs.stock_code, inputs.year and inputs.season are required." },
      { status: 400 },
    );
  }

  const inputs = {
    stock_code: stockCode,
    stock_name: body.inputs.stock_name?.trim() || stockCode,
    year: String(year),
    season: String(season),
    locale: body.inputs.locale || "zh-CN",
  };

  const cached = await fetchCachedFilingAnalysis(stockCode, year, season);
  if (!body.force && (cached?.summary || cached?.full_markdown)) {
    return NextResponse.json({
      analysis: {
        ...cached,
        code: stockCode,
        year,
        season,
      },
    });
  }

  let difyPayload: Record<string, unknown>;

  if (isAgentFilingWorkflow()) {
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

    difyPayload = (await difyResponse.json()) as Record<string, unknown>;
    if (!difyResponse.ok) {
      return NextResponse.json(
        { error: "Dify filing workflow failed.", detail: difyPayload },
        { status: 502 },
      );
    }
  } else {
    const difyResponse = await fetch(`${difyUrl}/chat-messages`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        inputs,
        query: FILING_QUERY,
        response_mode: "blocking",
        user: body.user || "twelvewin-web",
      }),
    });

    difyPayload = (await difyResponse.json()) as Record<string, unknown>;
    if (!difyResponse.ok) {
      return NextResponse.json(
        { error: "Dify filing chat failed.", detail: difyPayload },
        { status: 502 },
      );
    }
  }

  const answer = extractAgentAnswer(difyPayload);
  const parsed = parseFilingAnalysisPayload(
    answer ? { ...difyPayload, answer } : difyPayload,
  );

  if (parsed.error) {
    return NextResponse.json({ error: parsed.error, detail: difyPayload }, { status: 502 });
  }

  const result = {
    ...parsed,
    code: stockCode,
    year,
    season,
  };

  try {
    await saveFilingAnalysis(stockCode, year, season, result);
  } catch (error) {
    return NextResponse.json(
      {
        analysis: result,
        warning:
          error instanceof Error
            ? error.message
            : "Analysis completed but cache write failed.",
      },
      { status: 200 },
    );
  }

  return NextResponse.json({ analysis: result });
}
