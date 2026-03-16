#!/usr/bin/env bash
set -euo pipefail

# Prune only Docker builder cache. Never add volume-pruning flags here.

if ! command -v docker >/dev/null 2>&1; then
  echo "[dgx-docker-prune] docker is not installed or not on PATH." >&2
  exit 127
fi

echo "[dgx-docker-prune] Docker disk usage before prune:" >&2
docker system df >&2 || true

if docker buildx version >/dev/null 2>&1; then
  echo "[dgx-docker-prune] Running: docker buildx prune --all --force" >&2
  if docker buildx prune --all --force; then
    echo "[dgx-docker-prune] Docker disk usage after prune:" >&2
    docker system df >&2 || true
    exit 0
  fi
  echo "[dgx-docker-prune] buildx prune failed; falling back to docker builder prune." >&2
fi

echo "[dgx-docker-prune] Running: docker builder prune --all --force" >&2
docker builder prune --all --force

echo "[dgx-docker-prune] Docker disk usage after prune:" >&2
docker system df >&2 || true
