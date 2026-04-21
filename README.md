# Inbound Carrier Sales Agent

HappyRobot FDE take-home. A web-call inbound carrier sales agent for freight brokers, with FMCSA MC verification, deterministic 3-round rate negotiation, and a broker-facing dashboard.

- **Live dashboard:** https://carrier-sales-jo.fly.dev
- **Live API docs:** https://carrier-sales-jo.fly.dev/docs
- **HappyRobot workflow:** `platform.happyrobot.ai/fdejothiswaranarumugam/workflows/5jlf1pmyz038`
- **Video walkthrough:** _to be added_

## Stack

- **Voice + LLM:** HappyRobot platform (native Voice Agent, Classify, Extract nodes).
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + SQLite, single container.
- **Dashboard:** Next.js 15 App Router + Tailwind + Recharts, static export served by FastAPI.
- **Deploy:** Docker multi-stage, Fly.io `sjc` region, HTTPS auto.

## Quickstart (local)

```bash
cp .env.example .env.local
# Fill in API_KEY (random 64-hex) and FMCSA_WEBKEY
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
mkdir -p data
python -m scripts.seed_loads
./scripts/run_local.sh
# API: http://localhost:8080/healthz
```

## Deploy (Fly.io)

```bash
./scripts/deploy.sh
```

## API

| Method | Path | Auth |
|---|---|---|
| GET | `/carriers/verify?mc=XXXXX` | X-API-Key |
| GET | `/loads/search?origin=&destination=&equipment=&pickup_date=` | X-API-Key |
| GET | `/loads/{load_id}` | X-API-Key |
| POST | `/calls` | X-API-Key |
| GET | `/metrics` | X-API-Key |
| GET | `/healthz` | public |
| GET | `/` | public (dashboard) |

## Tests

```bash
pytest -v
```

## License

MIT.
