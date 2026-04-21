"use client";

import { useState } from "react";

import type { CallOut } from "@/lib/types";

function formatDelta(loadboard: number | null, agreed: number | null) {
  if (!loadboard || !agreed) return "-";
  const pct = ((agreed - loadboard) / loadboard) * 100;
  const sign = pct >= 0 ? "+" : "";
  return `${sign}${pct.toFixed(1)}%`;
}

function fmtTime(iso: string | null) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function CallsTable({ calls }: { calls: CallOut[] }) {
  const [openId, setOpenId] = useState<string | null>(null);

  if (calls.length === 0) {
    return (
      <div className="panel p-8 text-center text-slate-500 text-sm">
        No calls yet. Trigger a web call from the HappyRobot workflow to populate.
      </div>
    );
  }

  return (
    <div className="panel overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs uppercase tracking-wider text-slate-500 border-b border-slate-800">
            <th className="p-3">When</th>
            <th className="p-3">Carrier</th>
            <th className="p-3">MC</th>
            <th className="p-3">Load</th>
            <th className="p-3 text-right">Rate</th>
            <th className="p-3 text-right">Delta</th>
            <th className="p-3 text-center">Rounds</th>
            <th className="p-3">Outcome</th>
            <th className="p-3">Sentiment</th>
          </tr>
        </thead>
        <tbody>
          {calls.map((c) => {
            const isOpen = openId === c.call_id;
            return (
              <>
                <tr
                  key={c.call_id}
                  className="border-b border-slate-800 hover:bg-slate-900 cursor-pointer"
                  onClick={() => setOpenId(isOpen ? null : c.call_id)}
                >
                  <td className="p-3 text-slate-400 font-mono text-xs">
                    {fmtTime(c.started_at)}
                  </td>
                  <td className="p-3">{c.carrier_name ?? "-"}</td>
                  <td className="p-3 font-mono text-xs text-slate-400">
                    {c.mc_number ?? "-"}
                  </td>
                  <td className="p-3 font-mono text-xs text-slate-400">
                    {c.load_id ?? "-"}
                  </td>
                  <td className="p-3 text-right font-mono">
                    {c.final_agreed_rate
                      ? `$${c.final_agreed_rate.toFixed(0)}`
                      : c.loadboard_rate
                      ? `$${c.loadboard_rate.toFixed(0)}`
                      : "-"}
                  </td>
                  <td className="p-3 text-right font-mono text-xs">
                    {formatDelta(c.loadboard_rate, c.final_agreed_rate)}
                  </td>
                  <td className="p-3 text-center font-mono">
                    {c.negotiation_rounds ?? 0}
                  </td>
                  <td className="p-3 text-xs">
                    <span
                      className={
                        c.outcome === "booked"
                          ? "text-emerald-400"
                          : c.outcome === "carrier_ineligible"
                          ? "text-amber-400"
                          : "text-slate-400"
                      }
                    >
                      {c.outcome.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="p-3 text-xs text-slate-400">
                    {c.sentiment ?? "-"}
                  </td>
                </tr>
                {isOpen && c.transcript && (
                  <tr className="bg-slate-950 border-b border-slate-800">
                    <td
                      colSpan={9}
                      className="p-4 text-xs text-slate-400 whitespace-pre-wrap font-mono"
                    >
                      {c.transcript}
                    </td>
                  </tr>
                )}
              </>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
