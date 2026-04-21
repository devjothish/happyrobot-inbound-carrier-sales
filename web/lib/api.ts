"use client";

import type { Metrics } from "./types";

export const API_BASE = (typeof window !== "undefined"
  ? (window as unknown as { __API_BASE?: string }).__API_BASE
  : "") ?? "";

export async function fetchMetrics(apiKey: string): Promise<Metrics> {
  const base = API_BASE || "";
  const r = await fetch(`${base}/metrics`, {
    headers: { "X-API-Key": apiKey },
    cache: "no-store",
  });
  if (!r.ok) throw new Error(`metrics ${r.status}`);
  return r.json();
}
