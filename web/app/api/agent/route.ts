import { NextResponse } from "next/server";

import { getAgentStatus } from "@/lib/agent-config";

export async function GET() {
  return NextResponse.json(getAgentStatus());
}
