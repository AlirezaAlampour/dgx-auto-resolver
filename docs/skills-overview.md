# Skills Overview

Risk levels here describe operational impact if the skill is used incorrectly.

| Skill | Purpose | Trigger | Risk level | Notes |
| --- | --- | --- | --- | --- |
| `dgx-auto-resolver` | Repair missing Python imports in Dockerized apps without replacing the vendor GPU stack | `ModuleNotFoundError` or a pure Python missing-package `ImportError` during container startup | Medium | Generates `safe_requirements.txt` from a real boot path and protects accelerator packages |
| `dgx-docker-prune` | Reclaim Docker disk space by pruning builder cache only | `ENOSPC`, `no space left on device`, or explicit post-build cache cleanup | Medium | Never prunes volumes or host-mounted data under `/srv/ai/...` |
| `dgx-uma-memory-check` | Gate heavy runs on ARM64 UMA memory availability | Before starting a new container, benchmark, or memory-hungry model workload | Low | Uses `/proc/meminfo`, not `nvidia-smi`, and blocks work below `40 GB` available |
| `tail-safe-logs` | Read Docker logs without unbounded output | Crash debugging, recent error inspection, or temporary startup monitoring | Low | Requires explicit `--tail`, using `CONTAINER` placeholders in examples |
| `update-repo-map` | Maintain a short high-level `ARCHITECTURE.md` repo map | When `ARCHITECTURE.md` already exists or after material architecture changes | Low | Orientation aid only; never ground truth for implementation details |
