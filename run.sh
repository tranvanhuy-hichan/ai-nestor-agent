#!/usr/bin/env bash
# Tuong thich cu: ./run.sh [start|bg|stop|dev]  ->  dung lenh `nestor` (xem: nestor --help)
cd "$(dirname "$0")"
NESTOR=".venv/bin/nestor"
if [ ! -x "$NESTOR" ]; then
  echo "Chua cai Nestor. Chay: python3 -m venv .venv && .venv/bin/pip install -e app/backend" >&2
  exit 1
fi
case "${1:-start}" in
  start) exec "$NESTOR" start -f ;;   # foreground nhu truoc
  bg)    exec "$NESTOR" start ;;
  *)     exec "$NESTOR" "$@" ;;
esac
