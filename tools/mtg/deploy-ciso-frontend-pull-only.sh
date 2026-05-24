#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  deploy-ciso-frontend-pull-only.sh IMAGE [COMPOSE_DIR]

Example:
  deploy-ciso-frontend-pull-only.sh \
    ghcr.io/midtown-technology-group/ciso-assistant-community/frontend:mtg-4bfad1abc \
    /opt/ciso-assistant-poc

This script is intentionally pull-only. It never builds images on the app host.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

image="${1:-}"
compose_dir="${2:-/opt/ciso-assistant-poc}"

if [[ -z "$image" ]]; then
  usage >&2
  exit 2
fi

if [[ "$image" != *":"* && "$image" != *@sha256:* ]]; then
  echo "Refusing to deploy an untagged image: $image" >&2
  exit 2
fi

if [[ ! -f "$compose_dir/docker-compose.yml" ]]; then
  echo "Compose file not found: $compose_dir/docker-compose.yml" >&2
  exit 2
fi

if [[ "$image" == ghcr.io/* ]]; then
  docker pull "$image"
else
  docker image inspect "$image" >/dev/null
fi

cd "$compose_dir"
backup="docker-compose.yml.bak-frontend-$(date -u +%Y%m%dT%H%M%SZ)"
cp docker-compose.yml "$backup"

python3 - "$image" <<'PY'
from pathlib import Path
import sys

image = sys.argv[1]
path = Path("docker-compose.yml")
lines = path.read_text().splitlines()
in_frontend = False

for index, line in enumerate(lines):
    if line.startswith("  frontend:"):
        in_frontend = True
        continue
    if in_frontend and line.startswith("  ") and not line.startswith("    "):
        in_frontend = False
    if in_frontend and line.strip().startswith("image:"):
        indent = line[: len(line) - len(line.lstrip())]
        lines[index] = f"{indent}image: {image}"
        break
else:
    raise SystemExit("frontend image line not found")

path.write_text("\n".join(lines) + "\n")
PY

docker compose up -d frontend

docker inspect ciso-poc-frontend \
  --format 'image={{.Config.Image}} status={{.State.Status}} started={{.State.StartedAt}}'

echo "Backup: $compose_dir/$backup"
