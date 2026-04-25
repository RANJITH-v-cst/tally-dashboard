#!/usr/bin/env bash
# One-command local start for the Tally Dashboard.
#   ./start.sh                 # starts backend and frontend in dev mode
#   TALLY_URL=http://... ./start.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
  echo
  echo "[stop] Shutting down…"
  kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if ! command -v uv >/dev/null 2>&1; then
  echo "[setup] Installing uv (Python package manager)…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "[setup] Syncing backend deps…"
(cd "$ROOT/backend" && uv sync --quiet)

echo "[setup] Installing frontend deps…"
(cd "$ROOT/frontend" && [ -d node_modules ] || npm install --silent)

TALLY_URL_VALUE="${TALLY_URL:-http://localhost:9000}"
echo
echo "[start] Tally URL: $TALLY_URL_VALUE"
echo "[start] Backend:   http://localhost:8787  (docs at /docs)"
echo "[start] Dashboard: http://localhost:5173"
echo

(cd "$ROOT/backend" && TALLY_URL="$TALLY_URL_VALUE" uv run uvicorn app.main:app --host 127.0.0.1 --port 8787 --log-level warning) &
(cd "$ROOT/frontend" && npm run dev -- --host) &

wait
