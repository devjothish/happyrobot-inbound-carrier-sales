#!/usr/bin/env bash
# Deploys the carrier sales API + dashboard to Fly.io.
#
# Requirements:
#   - fly CLI authed (`fly auth whoami`)
#   - .env.local present with API_KEY and FMCSA_WEBKEY
#
# Usage:
#   ./scripts/deploy.sh

set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env.local ]]; then
  echo "ERROR: .env.local not found. Copy .env.example and fill in secrets." >&2
  exit 1
fi

set -a
source .env.local
set +a

: "${API_KEY:?API_KEY missing in .env.local}"
: "${FMCSA_WEBKEY:?FMCSA_WEBKEY missing in .env.local}"

APP_NAME="${FLY_APP:-carrier-sales-jo}"

if ! fly apps list 2>/dev/null | grep -q "^${APP_NAME}"; then
  echo "Creating Fly app: ${APP_NAME}"
  fly apps create "${APP_NAME}" --org personal
  fly volumes create carrier_sales_data --region sjc --size 1 --app "${APP_NAME}" --yes
fi

echo "Setting secrets on ${APP_NAME}"
fly secrets set \
  API_KEY="${API_KEY}" \
  FMCSA_WEBKEY="${FMCSA_WEBKEY}" \
  --app "${APP_NAME}" \
  --stage

echo "Deploying ${APP_NAME}"
fly deploy --app "${APP_NAME}" --yes

echo ""
echo "Deployed: https://${APP_NAME}.fly.dev"
echo "Health: curl https://${APP_NAME}.fly.dev/healthz"
