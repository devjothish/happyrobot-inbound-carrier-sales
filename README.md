# Inbound Carrier Sales Agent

HappyRobot FDE take-home. A web-call inbound carrier sales agent for freight brokers, with FMCSA MC verification, deterministic 3-round rate negotiation, and a broker-facing dashboard.

- **Live dashboard:** https://carrier-sales-jo.fly.dev
- **OpenAPI docs:** https://carrier-sales-jo.fly.dev/docs
- **HappyRobot workflow:** https://platform.happyrobot.ai/fdejothiswaranarumugam/workflows/5jlf1pmyz038/editor/nidou0lef3no
- **Build doc (Acme Logistics handoff):** [`docs/ACME_LOGISTICS_BUILD.md`](docs/ACME_LOGISTICS_BUILD.md)
- **Video walkthrough:** _added on submission_

## Accessing the dashboard

1. Open https://carrier-sales-jo.fly.dev
2. Paste the `X-API-Key` (shared privately with Carlos in the submission email) into the field top right.
3. Click **Reload**. The 6 tiles + recent calls populate from `/metrics`.

To hit the API directly:

```bash
curl "https://carrier-sales-jo.fly.dev/carriers/verify?mc=1515" -H "X-API-Key: <key>"
```

## Stack

- **Voice + LLM:** HappyRobot platform (native Voice Agent, Classify, Extract nodes).
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + SQLite, single container.
- **Dashboard:** Next.js 14 App Router + Tailwind + Recharts, static export served by FastAPI.
- **Deploy:** Docker multi-stage, Fly.io `sjc` region, HTTPS auto (Let's Encrypt via Fly).

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/carriers/verify?mc=XXXXX` | X-API-Key | FMCSA MC lookup, 24h cache |
| GET | `/loads/search?origin=&destination=&equipment_type=&pickup_date=` | X-API-Key | Top-3 matching loads |
| GET | `/loads/{load_id}` | X-API-Key | Single load |
| POST | `/calls` | X-API-Key | Workflow posts structured call record |
| GET | `/metrics` | X-API-Key | Aggregated dashboard data |
| GET | `/healthz` | public | Liveness |
| GET | `/` | public | Dashboard UI |

All endpoints listed in live OpenAPI at `/docs`.

## Quickstart (local)

```bash
git clone https://github.com/devjothish/happyrobot-inbound-carrier-sales.git
cd happyrobot-inbound-carrier-sales

cp .env.example .env.local
# Fill in:
#   API_KEY       (random 64-hex: python -c "import secrets; print(secrets.token_hex(32))")
#   FMCSA_WEBKEY  (request from https://mobile.fmcsa.dot.gov)

./scripts/run_local.sh
# http://localhost:8080/healthz
# http://localhost:8080/         (dashboard)
```

## Reproducing the deployment

One-shot deploy script:

```bash
brew install flyctl
fly auth login
./scripts/deploy.sh
```

The script:
1. Creates the Fly app + 1GB volume if missing.
2. Stages `API_KEY` and `FMCSA_WEBKEY` from `.env.local` as Fly secrets.
3. Builds the multi-stage Docker image and pushes to `registry.fly.io`.
4. Launches a single `shared-cpu-1x` machine in `sjc` with `auto_stop_machines=stop`.

Resulting URL: `https://<app-name>.fly.dev`.

Manual equivalent:

```bash
fly apps create carrier-sales-jo
fly volumes create carrier_sales_data --region sjc --size 1
fly secrets set API_KEY=... FMCSA_WEBKEY=...
fly deploy
```

## Tests

```bash
source .venv/bin/activate
pytest -v
# 27 tests: healthz, auth, loads, carriers (FMCSA), calls, metrics
```

## Repo layout

```
app/
  config.py          Pydantic settings
  deps.py            API key middleware
  db.py              SQLAlchemy engine + init
  models.py          Load / Carrier / Call
  schemas.py         Pydantic request/response types
  routers/
    loads.py         GET /loads/search, /loads/{id}
    carriers.py      GET /carriers/verify (FMCSA proxy + 24h cache)
    calls.py         POST /calls
    metrics.py       GET /metrics
  services/
    fmcsa.py         FMCSA HTTP client + response parse
  main.py            App wiring + static dashboard mount
web/                 Next.js dashboard (built to web/out -> served at /)
scripts/
  seed_loads.py      50 realistic seed loads
  deploy.sh          Fly.io deploy
  run_local.sh       Local dev runner
docs/
  ACME_LOGISTICS_BUILD.md        Customer-facing build doc
  HAPPYROBOT_WORKFLOW_SETUP.md   Platform configuration checklist
  email_to_carlos.md             Submission email draft
tests/               Pytest suite
Dockerfile           Multi-stage (node build -> python serve)
fly.toml             Fly.io config
```

## License

MIT.
