---
name: dgx-docker-prune
description: Reclaim Docker disk space on DGX-class systems by pruning only internal builder cache after ENOSPC or "no space left on device" failures, oversized image rebuilds, or explicit post-build cleanup requests. Use when Codex must free SSD space without deleting Docker volumes, named volumes, or any host-mounted data under /srv/ai/models, /srv/ai/cache/hf, or /srv/ai/outputs.
---

# DGX Docker Prune

Use this skill to recover disk space from Docker build cache while protecting host-mounted model, cache, and output data.

## Guardrails

- Treat `/srv/ai/models`, `/srv/ai/cache/hf`, and `/srv/ai/outputs` as untouchable host paths. Never delete files there and never target them through Docker cleanup commands.
- Never run `docker volume prune`, `docker system prune --volumes`, `docker rm -v`, or any command that removes named volumes or bind mounts.
- Default to pruning builder cache only. `docker system prune -f` is broader than builder-cache cleanup because it also removes unused containers, networks, and dangling images.
- If the user explicitly asks for broader Docker cleanup, stop and clarify that it goes beyond this skill's safe default.
- Prefer the bundled script `scripts/prune_builder_cache.sh` over ad hoc prune commands.

## Workflow

### 1. Confirm the problem fits this skill

- Use this skill for Docker build failures such as `ENOSPC` or `no space left on device`, or when a large rebuild has finished and builder cache cleanup is requested.
- If the pressure is clearly coming from data stored under `/srv/ai/models`, `/srv/ai/cache/hf`, or `/srv/ai/outputs`, stop. Those paths are outside this skill's scope.

### 2. Check Docker disk usage

- Run `docker system df` before pruning so you can verify builder cache is a meaningful source of disk pressure.
- If builder cache is not significant, report that instead of guessing with broader cleanup.

### 3. Prune only internal builder cache

- Run `scripts/prune_builder_cache.sh`.
- The script prefers `docker buildx prune --all --force` and falls back to `docker builder prune --all --force`.
- Do not add `--volumes`.
- Do not substitute `docker system prune -f` unless the user explicitly confirms broader cleanup.

### 4. Verify the result

- Run `docker system df` again and summarize the reclaimed space.
- If more cleanup is required after builder-cache pruning, explain that any broader Docker prune would widen scope beyond this skill's safe default.

## Resource

- `scripts/prune_builder_cache.sh`: Safe wrapper that prunes only Docker builder cache and shows Docker disk usage before and after cleanup.
