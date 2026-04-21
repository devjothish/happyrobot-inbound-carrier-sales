#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -d .venv ]]; then
  python3.12 -m venv .venv
  .venv/bin/pip install -U pip -q
  .venv/bin/pip install -r requirements-dev.txt -q
fi

if [[ ! -f data/app.db ]]; then
  mkdir -p data
  .venv/bin/python -m scripts.seed_loads
fi

set -a
[[ -f .env.local ]] && source .env.local
set +a

exec .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
