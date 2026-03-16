---
name: tail-safe-logs
description: Safely inspect Docker container logs without overrunning context. Use when Codex needs to read Docker logs, debug a crashed container, inspect recent errors, or monitor a booting or running service in the dgx-ai-stack or any similar Docker environment. This skill requires every `docker logs` command to include `--tail`, using `docker logs --tail 100 CONTAINER` for one-time reads and `docker logs --tail 50 -f CONTAINER` for temporary live monitoring.
---

# Tail Safe Logs

Use this skill to inspect container logs while protecting context size and avoiding unbounded log reads.

## Rules

- Never run a bare `docker logs` command.
- Always append `--tail` to every `docker logs` invocation.
- Use `docker logs --tail 100 CONTAINER` for one-time inspection of recent errors, crashes, or restarts.
- Use `docker logs --tail 50 -f CONTAINER` when watching a container boot or monitoring a running service interactively.
- Terminate follow mode as soon as the boot succeeds, the failure is clear, or the needed evidence has been captured.
- Resolve the real container name first if the user gives a Compose service name, project name, or partial identifier.
- Increase the tail size only when the smaller default does not answer the question, and still keep `--tail` explicit.

## Workflow

### 1. Identify the target container

- Use `docker ps --format '{{.Names}}'` for running containers.
- Use `docker ps -a --format '{{.Names}}'` when debugging a crash, restart loop, or exited container.
- Match the requested dgx-ai-stack service to the actual container name before reading logs.

### 2. Read recent logs safely

- Run `docker logs --tail 100 CONTAINER` to inspect recent failures or warnings.
- Summarize the recent lines first instead of immediately broadening the read.

### 3. Follow startup logs safely

- Run `docker logs --tail 50 -f CONTAINER` when the task requires watching a service start.
- Stop the follow session promptly once success or failure is established.

### 4. Escalate without dropping the guardrail

- If `100` lines are insufficient, choose a larger explicit tail such as `200` or `500`.
- Never replace a tailed command with an unbounded `docker logs` call.

## Response Pattern

- Report the exact tailed command used when summarizing logs.
- If follow mode was used, state why it was stopped.
