#!/usr/bin/env bash
# Desarrollo: API con recarga (127.0.0.1:8000) y Vite (localhost:5173). Ctrl+C detiene ambos.
set -e
cd "$(dirname "$0")"

.venv/bin/uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000 &
API=$!
(cd frontend && npm run dev) &
WEB=$!
trap 'kill $API $WEB 2>/dev/null' EXIT INT TERM
wait
