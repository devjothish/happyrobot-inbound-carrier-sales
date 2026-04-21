export type Outcome =
  | "booked"
  | "no_match"
  | "carrier_ineligible"
  | "negotiation_failed"
  | "carrier_walked"
  | "error";

export type Sentiment = "positive" | "neutral" | "negative";

export interface CallOut {
  call_id: string;
  started_at: string | null;
  ended_at: string | null;
  mc_number: string | null;
  carrier_name: string | null;
  load_id: string | null;
  loadboard_rate: number | null;
  final_agreed_rate: number | null;
  negotiation_rounds: number;
  outcome: Outcome;
  sentiment: Sentiment | null;
  duration_seconds: number | null;
  transcript: string | null;
  raw_extract: Record<string, unknown> | null;
}

export interface Metrics {
  total_calls: number;
  acceptance_rate: number;
  avg_negotiated_delta_pct: number;
  outcome_breakdown: Partial<Record<Outcome, number>>;
  mc_funnel: { verified: number; ineligible: number; not_found: number };
  sentiment_x_outcome: { sentiment: Sentiment; outcome: Outcome; count: number }[];
  avg_time_to_book_seconds: number;
  avg_negotiation_rounds: number;
  recent_calls: CallOut[];
}
