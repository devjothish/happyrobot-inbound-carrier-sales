# Loom Video Script - 5 min

**Goal:** Hit all three PDF asks (use case setup, short demo, dashboard) in under 5 minutes without rerecording.

**Setup before recording:**
- Tabs open: repo, HappyRobot workflow editor, dashboard (already authed), this script on a second monitor
- Terminal open at repo root
- Dashboard already has at least 2-3 real calls populated from the E2E runs
- Mic tested, 1080p, Loom Studio preferred

---

## Beat 1 - Intro + problem (0:00 - 0:30) [30s]

**Show:** Repo readme on screen.

> "Hey Carlos, Jo here. This is the HappyRobot FDE take-home - an inbound carrier sales agent for a hypothetical freight broker. Carriers call a web number, the agent verifies their MC with FMCSA, pitches a matching load, negotiates the rate under a policy, and books or walks. Everything runs on the HappyRobot platform plus a Python API and Next.js dashboard I deployed on Fly.io. Let me show you the pieces."

---

## Beat 2 - Use case setup / architecture (0:30 - 1:30) [60s]

**Show:** HappyRobot workflow editor (full canvas view).

> "Here's the workflow. Web call trigger into the inbound voice agent. Two tool nodes - verify_carrier and find_available_loads - both hit webhooks on my API. Classify node tags outcome and sentiment, Extract pulls structured fields, then a silent POST to /calls persists the record."

**Show:** Switch to VS Code / terminal, show `app/routers/` tree.

> "The API is five endpoints: /carriers/verify proxies FMCSA live with a 24h cache, /loads/search filters a seeded SQLite of 50 realistic loads, /calls is the webhook target, /metrics feeds the dashboard. All behind X-API-Key, HTTPS via Fly. One Docker image, multi-stage build, Next.js dashboard served at the root by FastAPI."

---

## Beat 3 - Live demo (1:30 - 3:30) [2:00]

**Show:** HappyRobot web call trigger.

> "Let's run a call. I'll play the carrier."

**Do:** Click web call, role-play the happy path.

> *Carrier:* "Hi, I'm looking for a load."
> *Agent:* "Hi, thanks for calling. Can I get your MC number?"
> *Carrier:* "MC-1515."
> *(Agent verifies, comes back with carrier name.)*
> *Carrier:* "I'm looking for a reefer out of the northeast."
> *(Agent pitches top match.)*
> *Carrier:* "I'll take it at the rate."
> *(Agent reads back, says the transfer line, ends call.)*

**Narrate over:**

> "Notice: FMCSA hit, carrier name read back, load pitched with rate, clean close. All of it ran through our webhooks - you'll see it land in the dashboard in a second."

**Optional 20s:** trigger a second call that goes to negotiation - carrier counters 5% below, agent meets halfway, books at round 2. Shows the 3-round policy working.

---

## Beat 4 - Dashboard walk (3:30 - 4:30) [60s]

**Show:** Dashboard after the call just completed.

> "Here's the broker console. Every tile maps to a broker decision. Top row:"

- **Acceptance rate:** "What percent of calls actually book. Trending this is how you catch whether loadboard rates are too aggressive."
- **Avg negotiated delta:** "Margin impact - what percent below loadboard we close at. If this goes below -5%, negotiation policy needs tightening."
- **Avg time-to-book:** "Carrier friction signal. Target under 4 minutes."

**Scroll to second row.**

- **Outcome breakdown:** "Six buckets - booked, no match, ineligible, negotiation failed, walked, error. Failure mode distribution at a glance."
- **MC funnel:** "FMCSA verification health. Spikes in not-found usually mean carriers gave DOT instead of MC."
- **Sentiment × outcome crosstab:** "The most interesting cell - positive sentiment AND no-book means carriers walked happy, which means we priced too high."

**Scroll to recent calls table.**

> "Last 20 calls, click any row for the transcript. You can see our live call just landed."

---

## Beat 5 - Close (4:30 - 5:00) [30s]

**Show:** Repo README.

> "Everything's public on GitHub, deploy is one shell script, 27 unit tests on the API. Build doc in the repo framed as an Acme Logistics handoff. The biggest call I made was keeping negotiation rules in the prompt - works for v1, but I'd move it to a pricing engine service for v2, happy to talk through that in the system design round. Thanks for the look."

---

## Fallback beats if short on time

- Skip the negotiation call (save 20s)
- Cut detailed sentiment explanation (save 15s)
- Trim architecture narration to "API + platform + dashboard, one container, Fly.io"

## Fallback if something breaks on camera

- If FMCSA 503s: "FMCSA rate limits occasionally - our cache handles repeat hits, first lookup sometimes flickers. Retry and it's green."
- If webhook 500s: show Fly logs briefly, note monitoring story.
- If dashboard lag: acknowledge, skip to repo tour.

## After recording

1. Trim dead air at both ends.
2. Add chapter markers in Loom (Intro / Architecture / Demo / Dashboard / Close).
3. Copy shareable URL into `docs/email_to_carlos.md` replacing `<LOOM_URL>`.
