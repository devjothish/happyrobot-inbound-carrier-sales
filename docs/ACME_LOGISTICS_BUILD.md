# Inbound Carrier Sales Agent - Build for Acme Logistics

**Status:** Production-ready POC, deployed at `https://carrier-sales-jo.fly.dev`
**Built by:** Jothiswaran Arumugam
**Timeline:** 3 engineering days (2026-04-20 through 2026-04-23)

## What this does

Carriers call Acme's inbound sales line. An AI voice agent answers, verifies their MC authority with FMCSA live, pitches a matching load from Acme's board, negotiates the rate inside Acme's policy, and books the deal. Every call is classified, extracted, and persisted so the ops team sees what's happening without listening to recordings.

Three people win here:

- **Carriers** get instant service outside business hours and a rate conversation that isn't "let me check with my manager."
- **Brokers** stop burning time on pre-qualification and stop losing margin to freelance negotiation. They see on one screen which calls booked, which walked, and at what delta.
- **Ops leaders** get real signal - acceptance rate, negotiated delta, sentiment-by-outcome - instead of a call log.

## How a call flows

```
Carrier dials web number
       │
       ▼  HappyRobot platform (voice + LLM)
  ┌────────────────────────────────────────────┐
  │ 1. Greeting, ask for MC                     │
  │ 2. verify_carrier tool ──► Acme API         │
  │                         └► FMCSA live       │
  │ 3. If ineligible: decline + end             │
  │ 4. Ask for lane/equipment                   │
  │ 5. find_available_loads ──► Acme API        │
  │ 6. If no match: callback offer + end        │
  │ 7. Pitch top load                           │
  │ 8. Negotiate (max 3 rounds, rule-bound)     │
  │ 9. Close at ≥ L-8%, or walk away            │
  │ 10. Classify (outcome + sentiment)          │
  │ 11. Extract (structured call fields)        │
  │ 12. POST /calls ──► Acme API                │
  └────────────────────────────────────────────┘
                       │
                       ▼
              Acme dashboard refreshes
```

Each call settles in under 4 minutes on the happy path. FMCSA lookups run in ~800 ms; our service caches them 24 hours so the second call from the same carrier is instant.

## The numbers that matter

A broker does not need vanity charts. They need decisions. Here's what each dashboard tile unlocks:

| Tile | What it is | What a broker does with it |
|---|---|---|
| **Acceptance rate** | booked ÷ total | If this drops week-over-week, either loads are mispriced or the agent's negotiation is leaking. |
| **Avg negotiated delta** | (final - loadboard) / loadboard, booked only | Margin dashboard. If this trends below -5%, loadboard rates are too aggressive. |
| **Avg time-to-book** | duration for booked calls | Longer calls = carrier friction or too much back-and-forth. Target under 4:00. |
| **Outcome breakdown** | 6-bucket distribution | Quick read on failure modes - lots of `carrier_ineligible` means MC lists are stale, lots of `negotiation_failed` means policy is too tight. |
| **MC funnel** | verified / ineligible / not found | Raw FMCSA health. Spikes in `not_found` usually mean a carrier gave a DOT instead of MC. |
| **Sentiment × outcome** | crosstab | The cell worth watching: *positive sentiment + no-book*. Those are priced too high - happy carriers walked on price. |

Vanity metrics we deliberately did not build: call count, average call length across all outcomes, agent "helpfulness" score. They feel like dashboards but don't change what a broker does Monday morning.

## Negotiation policy

Loadboard rate is the anchor. Call it `L`.

```
Max 3 rounds. Floor: L - 10%. Target close: L - 8% or better.

Round 1:
  carrier offer ≥ L         → accept
  carrier offer < L - 20%   → decline politely, requote at L - 3%
  otherwise                 → propose midpoint between offer and L

Round 2: halve the gap between current standing offer and L.

Round 3 (final):
  take max(carrier offer, L - 8%)
  if carrier still below that → walk away
```

These rules live in the agent's prompt today. **Why in the prompt and not a pricing service?** Because it's a POC, because the rules are 10 lines, and because Carlos is testing whether I can ship, not whether I can over-engineer. Next iteration (see below) replaces this with a pricing engine.

## Integration surface

Five endpoints. One static API key in `X-API-Key`. That's the whole auth model.

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/carriers/verify?mc=X` | Live FMCSA proxy, 24h cache |
| `GET`  | `/loads/search` | Filter loadboard, top-3 results |
| `GET`  | `/loads/{id}` | Single load detail |
| `POST` | `/calls` | Workflow posts structured call record |
| `GET`  | `/metrics` | Dashboard data |
| `GET`  | `/healthz` | Liveness |
| `GET`  | `/` | Dashboard UI |

**Why API key over JWT for v1?** JWT buys you nothing when there's exactly one server-to-server caller (HappyRobot). It costs you a token-refresh path you don't need. When Acme adds a second caller or a multi-tenant model, we move to JWT in a half-day change. Same reason we shipped SQLite instead of Postgres - one machine, one concurrent writer, no ops pain.

## Ops

One Docker image. Multi-stage build: Node builds the Next.js dashboard, Python serves both the API and the static dashboard. 54 MB image, 512 MB memory, scale-to-zero on idle. Fly.io `sjc` region for latency to HappyRobot's infra.

- **Deploy:** `./scripts/deploy.sh` - creates the app, sets secrets, pushes the image. Reproducible.
- **Secrets:** `API_KEY`, `FMCSA_WEBKEY` injected via `fly secrets`. Never in git history, never in image.
- **Database:** SQLite on a 1GB Fly volume. Zero ops cost until we exceed ~10k calls/day. Migration path to managed Postgres is mechanical when needed (SQLAlchemy abstracts dialect).
- **Observability:** Fly's built-in logs + healthcheck. For prod we'd add Sentry and structured JSON logs.

## What I would build next

Ranked by impact-to-effort:

1. **Pricing engine service.** Today rates live in loadboard + prompt. Move to a `/pricing/quote` endpoint that returns `{floor, target, walk_away}` based on equipment + lane + current market index. Agent becomes dumber, pricing becomes explainable and tunable without redeploying the prompt. ~2 days.

2. **Carrier scorecard table.** Log every interaction per MC (bookings, walk-aways, sentiment history). Next call from that carrier, pitch differently - known good carriers get first look at spot loads, known walkers get a lower initial anchor. ~1 day once we have >100 calls.

3. **Slack/Notion webhook on high-value bookings.** POST `/calls` branches on `final_agreed_rate > threshold` and pings dispatch Slack. Brokers know 30 seconds after the call ends, not tomorrow morning. ~2 hours.

4. **Transcript embeddings + search.** Every transcript gets embedded at write time (OpenAI or Bedrock). Broker types "who asked about reefer capacity to Florida last week" - gets the 5 most relevant calls. ~1 day.

5. **A/B the negotiation policy.** Tag each call with policy version. Compare acceptance rate × margin delta across versions. This is the real value of the prompt-first design - policies are cheap to swap. ~half-day once we have 200+ calls/policy.

## Known cuts (non-goals for v1)

- **User auth / multi-tenant.** One broker, one key. Good enough to demo. JWT + orgs is a week we don't have and don't need yet.
- **Real phone numbers.** PDF says web call only. Twilio/HappyRobot handle the SIP pivot when ready.
- **CI/CD pipeline.** One engineer, manual deploys fine. Reproducible via `deploy.sh`.
- **Managed DB.** SQLite is right until we have concurrent writers or cross-region reads.
- **Custom classification model.** HappyRobot's native Classify node is already tuned for voice transcripts. Hand-rolling a Claude call is engineering to impress, not to ship.
- **Dashboard interactivity beyond basics.** No date range filter, no carrier drill-down. Could add in a day - cut because a broker looking at "today's calls" doesn't need 20 ways to slice them.

---

*Anything not covered here is either in the repo README or I'd be happy to walk through on a call.*
