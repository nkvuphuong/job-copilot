#!/bin/sh
# Seed /data on first run, then serve the UI or pass args through to the CLI.
#   docker compose run --rm jc status     -> CLI on the same DB
set -eu
DATA="${JC_DATA:-/data}"

if [ "$(id -u)" = 0 ]; then
  mkdir -p "$DATA"
  chown -R app:app "$DATA"
  exec setpriv --reuid app --regid app --init-groups "$0" "$@"
fi

if ! mkdir -p "$DATA/jobs" 2>/dev/null; then
  echo "error: $DATA is not writable by uid $(id -u) — rebuild with:" >&2
  echo "  docker compose build --build-arg UID=$(id -u) --build-arg GID=$(id -g)" >&2
  exit 1
fi
for d in cv prep offers sync; do mkdir -p "$DATA/$d"; done

# Templates only fill empty slots; an existing profile/DB is never overwritten.
[ -e "$DATA/profile.md" ] || cp /app/seeds/profile.example.md "$DATA/profile.md"
[ -e "$DATA/jobs/_example.md" ] || cp /app/seeds/jobs/_example.md "$DATA/jobs/"
[ -e "$DATA/cv/_example-en.md" ] || cp /app/seeds/cv/_example-en.md "$DATA/cv/"
[ -e "$DATA/prep/_example.md" ] || cp /app/seeds/prep/_example.md "$DATA/prep/"
[ -e "$DATA/offers/_example.md" ] || cp /app/seeds/offers/_example.md "$DATA/offers/"
[ -e "$DATA/sync/_example.md" ] || cp /app/seeds/sync/_example.md "$DATA/sync/"

DB="$DATA/jobcopilot.db"
python3 /app/tools/jobcopilot/cli.py --db "$DB" init >/dev/null

if [ "${1:-serve}" = "serve" ]; then
  exec python3 /app/tools/jobcopilot/server.py --db "$DB"
fi
exec python3 /app/tools/jobcopilot/cli.py --db "$DB" "$@"
