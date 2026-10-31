#!/usr/bin/env bash
# Copy this machine's local data (gitignored) into the Docker volume, so the
# container shows your existing jobs instead of an empty DB.
#
#   ./scripts/docker-import.sh          # refuses if the volume already has a DB
#   ./scripts/docker-import.sh --force  # overwrite
#
# Nothing leaves the machine: the data goes straight into the local volume.
set -euo pipefail
cd "$(dirname "$0")/.."

IMG=jobcopilot:local
VOL=jobcopilot-data
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

docker image inspect "$IMG" >/dev/null 2>&1 || {
  echo "image $IMG missing — run: docker compose build" >&2; exit 1
}
# Create the volume through compose (with its labels) so later `docker compose`
# commands don't warn that it "was not created by Docker Compose".
docker volume inspect "$VOL" >/dev/null 2>&1 || docker compose up --no-start >/dev/null 2>&1
docker volume inspect "$VOL" >/dev/null

if [ "$FORCE" = 0 ] && docker run --rm -v "$VOL":/data --entrypoint sh "$IMG" \
     -c '[ -f /data/jobcopilot.db ]' >/dev/null 2>&1; then
  echo "volume $VOL already has a DB — re-run with --force to overwrite" >&2
  exit 1
fi

SRC="$(mktemp -d)"
trap 'rm -rf "$SRC"' EXIT
# cli backup = consistent copy even while the host server holds the DB open
# (a plain cp would miss the -wal sidecar).
python3 tools/jobcopilot/cli.py backup --out "$SRC/jobcopilot.db" >/dev/null
for d in jobs cv prep offers sync; do
  if [ -d "$d" ]; then cp -a "$d" "$SRC/"; fi
done
if [ -f profile.md ]; then cp -a profile.md "$SRC/"; fi

docker run --rm -v "$VOL":/data -v "$SRC":/src:ro --entrypoint sh "$IMG" -c 'cp -a /src/. /data/'
echo "imported into volume $VOL:"
docker compose run --rm jc report | python3 -c 'import sys,json; d=json.load(sys.stdin); print("  funnel:", d["funnel"])'
