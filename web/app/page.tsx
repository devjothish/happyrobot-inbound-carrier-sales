"use client";

import { useEffect, useState } from "react";

import { CallsTable } from "@/components/CallsTable";
import { MCFunnel, OutcomeBars, SentimentHeatmap } from "@/components/Charts";
import { Tile } from "@/components/Tile";
import { fetchMetrics } from "@/lib/api";
import type { Metrics } from "@/lib/types";

function pct(n: number) {
  return `${(n * 100).toFixed(1)}%`;
}

function mmss(seconds: number) {
  if (!seconds) return "-";
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function Dashboard() {
  const [apiKey, setApiKey] = useState<string>("");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("apiKey");
    if (saved) setApiKey(saved);
  }, []);

  async function load(k: string) {
    if (!k) return;
    setLoading(true);
    setError(null);
    try {
      const m = await fetchMetrics(k);
      setMetrics(m);
      localStorage.setItem("apiKey", k);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (apiKey) load(apiKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey]);

  return (
    <main className="min-h-screen px-6 py-8 max-w-7xl mx-auto">
      <header className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-medium tracking-tight">Carrier Sales</h1>
          <p className="text-sm text-slate-500 mt-1">
            Broker console. Real-time view of inbound calls from the HappyRobot
            voice agent.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="password"
            placeholder="X-API-Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="panel px-3 py-1.5 text-sm font-mono w-64 outline-none focus:border-sky-500"
          />
          <button
            onClick={() => load(apiKey)}
            className="px-3 py-1.5 text-sm bg-sky-500 text-slate-950 rounded font-medium hover:bg-sky-400"
          >
            {loading ? "..." : "Reload"}
          </button>
        </div>
      </header>

      {error && (
        <div className="panel p-4 mb-6 border-rose-500/40 text-rose-300 text-sm">
          Error: {error}. Check your X-API-Key.
        </div>
      )}

      {!metrics && !error && (
        <div className="panel p-8 text-center text-slate-500 text-sm">
          Enter X-API-Key above to load dashboard.
        </div>
      )}

      {metrics && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Tile
              label="Acceptance Rate"
              value={pct(metrics.acceptance_rate)}
              hint={`${
                metrics.outcome_breakdown.booked ?? 0
              } booked of ${metrics.total_calls} calls`}
              tone={metrics.acceptance_rate >= 0.3 ? "good" : "neutral"}
            />
            <Tile
              label="Avg Negotiated Delta"
              value={`${
                metrics.avg_negotiated_delta_pct >= 0 ? "+" : ""
              }${(metrics.avg_negotiated_delta_pct * 100).toFixed(2)}%`}
              hint="Final rate vs loadboard, booked calls only. Negative = margin compression."
              tone={metrics.avg_negotiated_delta_pct >= -0.05 ? "good" : "bad"}
            />
            <Tile
              label="Avg Time to Book"
              value={mmss(metrics.avg_time_to_book_seconds)}
              hint={`Across ${
                metrics.outcome_breakdown.booked ?? 0
              } booked calls. Target under 4:00.`}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Tile label="Outcome Breakdown">
              <OutcomeBars breakdown={metrics.outcome_breakdown} />
            </Tile>
            <Tile label="MC Eligibility Funnel">
              <MCFunnel funnel={metrics.mc_funnel} />
              <div className="text-xs text-slate-500 mt-3">
                Avg negotiation rounds:{" "}
                <span className="font-mono text-slate-300">
                  {metrics.avg_negotiation_rounds.toFixed(1)}
                </span>
              </div>
            </Tile>
            <Tile
              label="Sentiment × Outcome"
              hint="Happy carriers who didn't book = priced too high."
            >
              <SentimentHeatmap cells={metrics.sentiment_x_outcome} />
            </Tile>
          </div>

          <h2 className="metric-label mt-8 mb-3">Recent Calls</h2>
          <CallsTable calls={metrics.recent_calls} />

          <footer className="text-xs text-slate-600 mt-10 pb-6">
            HappyRobot FDE take-home · Jothiswaran Arumugam · 2026
          </footer>
        </>
      )}
    </main>
  );
}
