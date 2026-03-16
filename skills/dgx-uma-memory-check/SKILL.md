---
name: dgx-uma-memory-check
description: Check available shared UMA memory on DGX Spark, DGX Station, and similar ARM64 UMA systems before Codex starts a new Docker container, runs a heavy test or benchmark, or deploys a memory-hungry model such as Wan 2.1 or F5-TTS. Use when Codex must gate work on host memory availability and must avoid `nvidia-smi` memory checks on architectures where GPU memory reporting is unsupported.
---

# DGX UMA Memory Check

Apply this guardrail before launching memory-sensitive work on ARM64 UMA systems.

## Rules

- Never use `nvidia-smi` to check memory availability on these systems. Treat any plan to query GPU memory with `nvidia-smi` as incorrect and replace it with a `/proc/meminfo` check.
- Read available memory with `cat /proc/meminfo | grep MemAvailable`.
- Convert the reported kilobytes to gigabytes by dividing by `1024 * 1024`.
- Round to one decimal place unless the task requires more precision.
- Compare the result against a hard minimum of `40 GB` before starting the workload.

## Workflow

1. Run the canonical check:

```bash
mem_kb="$(cat /proc/meminfo | grep MemAvailable | awk '{print $2}')"
mem_gb="$(awk -v kb="$mem_kb" 'BEGIN {printf "%.1f", kb/1024/1024}')"
printf 'MemAvailable: %s kB (%s GB)\n' "$mem_kb" "$mem_gb"
```

2. Evaluate the result:
- If `mem_gb` is at least `40.0`, proceed.
- If `mem_gb` is below `40.0`, stop before starting the container, heavy test, or model deployment.

3. Reclaim memory before retrying:
- If the host has `ai-idle-manager.service` installed, start or restart it to stop warm containers.
- Prefer this command for an immediate check cycle:

```bash
sudo systemctl restart ai-idle-manager.service
```

- Wait at least one service interval, typically about `60` seconds, then rerun the canonical memory check.

4. Escalate if memory remains low:
- Halt and warn the user with the measured `MemAvailable` value in both `kB` and `GB`.
- State that the machine uses UMA memory and that the workload must not proceed below `40 GB` available memory.
- If `ai-idle-manager.service` is unavailable or insufficient, ask the user before stopping containers manually or continuing anyway.

## Response Pattern

- Report the measured memory before starting work.
- If memory is below threshold, explain that the guardrail blocked the run and mention any recovery action taken.
- After a recovery attempt, report the follow-up measurement and whether it is now safe to proceed.
