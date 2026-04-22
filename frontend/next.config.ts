import path from "node:path";
import dotenv from "dotenv";
import type { NextConfig } from "next";

dotenv.config({ path: path.resolve(process.cwd(), "../.env") });

const isDevelopment = process.env.NODE_ENV !== "production";

if (
  isDevelopment &&
  !process.env.NEXT_PUBLIC_GO_GRAPHQL_API_URL &&
  !process.env.NEXT_PUBLIC_GRAPHQL_API_URL
) {
  process.env.NEXT_PUBLIC_GRAPHQL_API_URL = "http://localhost:8000/graphql";
}

const nextConfig: NextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.resolve(process.cwd(), ".."),
};

export default nextConfig;
