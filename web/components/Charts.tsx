"use client";

import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { Metrics, Outcome } from "@/lib/types";

const OUTCOME_COLORS: Record<Outcome, string> = {
  booked: "#34d399",
  no_match: "#94a3b8",
  carrier_ineligible: "#fbbf24",
  negotiation_failed: "#f87171",
  carrier_walked: "#fb7185",
  error: "#ef4444",
};

export function OutcomeBars({
  breakdown,
}: {
  breakdown: Metrics["outcome_breakdown"];
}) {
  const data = (Object.keys(breakdown) as Outcome[]).map((k) => ({
    outcome: k.replace(/_/g, " "),
    key: k,
    count: breakdown[k] ?? 0,
  }));
  if (data.length === 0) {
    return <div className="text-sm text-slate-500">No calls yet.</div>;
  }
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 8, right: 0, left: -20, bottom: 4 }}>
        <XAxis
          dataKey="outcome"
          stroke="#8b8f98"
          tick={{ fontSize: 11 }}
          interval={0}
          angle={-15}
          textAnchor="end"
          height={50}
        />
        <YAxis stroke="#8b8f98" tick={{ fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{
            background: "#14161a",
            border: "1px solid #23262c",
            color: "#e6e7eb",
          }}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((d) => (
            <Cell key={d.key} fill={OUTCOME_COLORS[d.key as Outcome] ?? "#8b8f98"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MCFunnel({ funnel }: { funnel: Metrics["mc_funnel"] }) {
  const total = funnel.verified + funnel.ineligible + funnel.not_found;
  const bar = (label: string, val: number, color: string) => {
    const pct = total > 0 ? (val / total) * 100 : 0;
    return (
      <div key={label}>
        <div className="flex justify-between text-xs">
          <span className="text-slate-400">{label}</span>
          <span className="font-mono text-slate-300">{val}</span>
        </div>
        <div className="h-2 bg-slate-800 rounded overflow-hidden mt-1">
          <div
            className="h-full"
            style={{ width: `${pct}%`, background: color }}
          />
        </div>
      </div>
    );
  };
  return (
    <div className="flex flex-col gap-3 mt-2">
      {bar("Verified", funnel.verified, "#34d399")}
      {bar("Ineligible", funnel.ineligible, "#fbbf24")}
      {bar("Not found", funnel.not_found, "#ef4444")}
    </div>
  );
}

export function SentimentHeatmap({
  cells,
}: {
  cells: Metrics["sentiment_x_outcome"];
}) {
  const sentiments: ("positive" | "neutral" | "negative")[] = [
    "positive",
    "neutral",
    "negative",
  ];
  const outcomes: Outcome[] = [
    "booked",
    "no_match",
    "carrier_ineligible",
    "negotiation_failed",
    "carrier_walked",
    "error",
  ];
  const lookup = new Map<string, number>();
  let max = 0;
  for (const c of cells) {
    lookup.set(`${c.sentiment}|${c.outcome}`, c.count);
    if (c.count > max) max = c.count;
  }

  const cellColor = (n: number) => {
    if (n === 0) return "#14161a";
    const alpha = Math.min(1, 0.15 + (n / Math.max(1, max)) * 0.85);
    return `rgba(125, 211, 252, ${alpha})`;
  };

  return (
    <div className="mt-2 overflow-x-auto">
      <table className="text-xs">
        <thead>
          <tr>
            <th className="p-1 text-left text-slate-500 font-normal"></th>
            {outcomes.map((o) => (
              <th
                key={o}
                className="p-1 text-slate-500 font-normal rotate-[-20deg] whitespace-nowrap"
              >
                {o.replace(/_/g, " ")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sentiments.map((s) => (
            <tr key={s}>
              <td className="pr-3 text-slate-400 capitalize text-right">{s}</td>
              {outcomes.map((o) => {
                const n = lookup.get(`${s}|${o}`) ?? 0;
                return (
                  <td
                    key={o}
                    className="text-center font-mono"
                    style={{
                      background: cellColor(n),
                      width: 52,
                      height: 28,
                      border: "1px solid #23262c",
                      color: n > max * 0.5 ? "#0b0c0e" : "#e6e7eb",
                    }}
                  >
                    {n > 0 ? n : ""}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
