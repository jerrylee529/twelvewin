import type { NextConfig } from "next";

const apiUrl = process.env.API_URL || "http://127.0.0.1:8090";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
