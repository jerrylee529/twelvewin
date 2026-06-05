import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const key = process.env.TW_RESEARCH_API_KEY?.trim();
  if (!key || !request.nextUrl.pathname.startsWith("/api/v1/")) {
    return NextResponse.next();
  }

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("X-Twelvewin-Api-Key", key);

  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

export const config = {
  matcher: "/api/v1/:path*",
};
