export function Tile({
  label,
  value,
  hint,
  tone = "neutral",
  children,
}: {
  label: string;
  value?: string | number;
  hint?: string;
  tone?: "good" | "bad" | "neutral";
  children?: React.ReactNode;
}) {
  const toneColor =
    tone === "good"
      ? "text-emerald-400"
      : tone === "bad"
      ? "text-rose-400"
      : "text-slate-100";
  return (
    <div className="panel p-5 flex flex-col gap-2">
      <div className="metric-label">{label}</div>
      {value !== undefined && (
        <div className={`metric-big ${toneColor}`}>{value}</div>
      )}
      {hint && <div className="text-xs text-slate-500">{hint}</div>}
      {children}
    </div>
  );
}
