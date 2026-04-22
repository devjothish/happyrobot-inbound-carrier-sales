# Email to Carlos Becker

**To:** c.becker@happyrobot.ai
**CC:** erik@happyrobot.ai, will.katae@happyrobot.ai *(confirm exact recruiter emails with Jo before sending)*
**Subject:** HappyRobot FDE take-home - Jothiswaran Arumugam

---

Hi Carlos,

Shipping the inbound carrier sales take-home. Live at https://carrier-sales-jo.fly.dev.

Deliverables:

- **Dashboard:** https://carrier-sales-jo.fly.dev *(use the X-API-Key in the API doc; I can also share directly if easier)*
- **Workflow:** https://platform.happyrobot.ai/fdejothiswaranarumugam/workflows/5jlf1pmyz038
- **Repo (public):** https://github.com/devjothish/happyrobot-inbound-carrier-sales
- **Build doc** *(framed as an "Acme Logistics" handoff):* `docs/ACME_LOGISTICS_BUILD.md` in the repo
- **5-min walkthrough:** <LOOM_URL>

Quick notes on choices:

- Used HappyRobot's native Classify + Extract nodes rather than hand-rolling an LLM classification call. Using the platform the way it's designed felt like the right signal for an FDE round, and the native nodes are tuned better than whatever I'd write in a day.
- FMCSA lookups cached 24h in SQLite to protect against rate limits and keep repeat calls from the same carrier sub-second.
- Negotiation rules live in the Prompt node (3-round caps, floor at loadboard - 10%, target ≥ loadboard - 8%). Deterministic enough to demo, and I'd love to walk through how I'd replace this with a proper pricing engine service in the system-design round.
- One Docker image on Fly.io `sjc` for latency; HTTPS by default; API-key auth sufficient for a single server-to-server caller. JWT + multi-tenant is where this grows next, not where it starts.

Happy to demo on a call anytime this week. The 3 test scenarios I'd walk through are happy-path (accept at loadboard), negotiation close, and MC reject.

Best,
Jo

Jothiswaran Arumugam
jothiswaran2604@gmail.com
linkedin.com/in/jothiswaran-arumugam
