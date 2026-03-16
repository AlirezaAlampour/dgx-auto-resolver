---
name: update-repo-map
description: Maintain a short root-level `ARCHITECTURE.md` as a high-level orientation map for multi-service repositories. Use when Codex starts work in a repo that already has `ARCHITECTURE.md`, or when a task materially changes system structure such as adding, removing, renaming, splitting, or rewiring services. The map is an orientation aid only, never ground truth, and should be refreshed only after material architecture changes.
---

# Update Repo Map

Use this skill to keep `ARCHITECTURE.md` as a compact repo map that helps future Codex runs get bearings quickly without rereading the whole repository.

## Core Rule

- Read `ARCHITECTURE.md` first if it exists.
- Use it only as a high-level guide to narrow which files need inspection.
- Verify any implementation-critical detail from source files before acting.
- Treat `ARCHITECTURE.md` as orientation only, never as ground truth for exact behavior.

## When To Use

Use this skill when:

- starting work in a multi-service repo that already contains `ARCHITECTURE.md`
- a service is added, removed, renamed, split, or merged
- Dockerfile locations or build contexts change
- ports, routes, queues, internal APIs, or service wiring change
- infrastructure dependencies change, such as Redis, databases, gateways, supervisors, workers, or shared mounts
- the user explicitly asks to map the repository

Do not use this skill for:

- small single-service repos
- tiny bug fixes with no architecture impact
- internal refactors that do not change service boundaries or wiring
- documentation edits unrelated to structure

## Workflow

### 1. Read the existing map first

- Open `<repo>/ARCHITECTURE.md` first if it exists.
- Use it to decide which manifests and service folders actually need inspection.
- If the map is missing, stale, or clearly incomplete, rebuild it from source files.

### 2. Inspect only high-signal files

Prefer concise, top-level sources such as:

- `docker-compose*.yml`
- `compose.yml`
- `Dockerfile*`
- service-level `README.md`
- `package.json`
- `pyproject.toml`
- `requirements*.txt`
- Helm charts or Kubernetes manifests when present

Avoid broad file-by-file exploration unless the repo structure cannot be understood from these sources.

### 3. Update only the architecture-level facts

Refresh or create `<repo>/ARCHITECTURE.md` with only high-level facts:

- repo overview
- deployable services/components
- path to each service
- Dockerfile or build context location
- main communication paths
- primary dependencies
- major shared infrastructure

Omit low-level implementation details.
If something is uncertain, mark it as inferred or leave it out.

## Required Contents

`ARCHITECTURE.md` should include:

1. `# Architecture`
2. `## Overview`
3. `## Services`
4. `## Communication`
5. `## Shared Infrastructure` or `## Infrastructure`

For `## Services`, prefer a compact table like:

`Service | Path | Dockerfile | Exposes / Talks To | Primary Dependencies`

## Quality Bar

- Optimize for orientation, not exhaustiveness.
- Keep it short enough to scan in under a minute.
- Prefer compact bullets or a small table over long prose.
- Use repository terminology consistently.
- Do not duplicate README text.
- Do not include speculative details as facts.
- If the repo is not truly microservice-based, map the real deployable units and say so explicitly.

## Maintenance Discipline

Refresh `ARCHITECTURE.md` only when structure changes materially.

Material changes include:

- service lifecycle changes
- new or removed service
- changed port/API/queue wiring
- changed Dockerfile/build context
- changed shared infrastructure or major dependency edges

Do not refresh it for ordinary feature work unless the system shape changed.

## How Future Codex Should Use It

When entering the repo:

1. Read `ARCHITECTURE.md`
2. Form a narrow hypothesis about which files matter
3. Verify exact details from source files before editing
4. Refresh `ARCHITECTURE.md` only if the task changed architecture
