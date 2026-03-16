# dgx-auto-resolver

`dgx-auto-resolver` is the canonical home for two related pieces of DGX workflow tooling:

- the resolver that repairs missing Python imports without replacing a vendor-tuned accelerator stack
- the reusable custom Codex skills that add guardrails for DGX, ARM64 UMA, and Docker-heavy workflows

This repository is meant for DGX Spark, DGX Station, and similar environments where `torch`, `torchvision`, CUDA, and vendor plugins are already correct and should not be casually upgraded during troubleshooting.

## Why This Exists

On DGX-class systems, broad dependency installs can easily destabilize a working container:

- ARM64 and UMA systems have platform-specific constraints
- vendor images often ship with tightly matched PyTorch and CUDA builds
- Docker cleanup and logging commands can be safe or destructive depending on how they are used
- repo maps are useful for orientation, but they must not replace source inspection

The resolver and bundled skills turn those lessons into repeatable guardrails.

## Repository Layout

```text
dgx-auto-resolver/
  README.md
  resolve_deps.py
  resolver/
    __init__.py
    resolve_deps.py
  skills/
    dgx-auto-resolver/
    dgx-docker-prune/
    dgx-uma-memory-check/
    tail-safe-logs/
    update-repo-map/
  docs/
    skills-overview.md
```

`resolver/resolve_deps.py` is the canonical resolver source. The root `resolve_deps.py` file remains as a compatibility entrypoint for existing usage.

## Resolver

The resolver is a narrow repair tool for Dockerized Python applications that fail on missing imports:

1. Probe the current `torch` and `torchvision` versions.
2. Write protected pins to `constraints.txt`.
3. Start the target script.
4. If startup fails with `ModuleNotFoundError`, install only the missing user-space package.
5. Repeat until the app boots cleanly.
6. Freeze the final environment to `safe_requirements.txt`.

It refuses to auto-install or replace protected accelerator packages such as `torch`, `torchvision`, `torchaudio`, `triton`, `xformers`, `nvidia*`, or `cuda*`.

### Basic Usage

```bash
python resolve_deps.py app.py
```

```bash
python resolve_deps.py --cwd /workspace app.py -- --host 0.0.0.0 --port 8080
```

You can also call the canonical source directly:

```bash
python resolver/resolve_deps.py app.py
```

## Included Skills

### Operational Guardrails

- `dgx-auto-resolver`: guides safe repair of containerized Python import failures without replacing the DGX GPU stack
- `dgx-docker-prune`: prunes Docker builder cache without touching volumes or protected host-mounted data
- `dgx-uma-memory-check`: blocks heavy work on UMA systems when `MemAvailable` is below the required threshold
- `tail-safe-logs`: enforces explicit `docker logs --tail` usage to keep troubleshooting bounded

### Repo And Documentation Helpers

- `update-repo-map`: maintains a short `ARCHITECTURE.md` only as a high-level orientation aid; it is not ground truth and should only be refreshed after material architecture changes

More detail is in [docs/skills-overview.md](/home/xxfactionsxx/dgx-auto-resolver/docs/skills-overview.md).

## Install The Skills Into Codex

Copy the skill folders:

```bash
mkdir -p "$HOME/.codex/skills"
for skill in \
  dgx-auto-resolver \
  dgx-docker-prune \
  dgx-uma-memory-check \
  tail-safe-logs \
  update-repo-map
do
  cp -a "skills/$skill" "$HOME/.codex/skills/"
done
```

Or symlink them from this repo:

```bash
mkdir -p "$HOME/.codex/skills"
for skill in \
  dgx-auto-resolver \
  dgx-docker-prune \
  dgx-uma-memory-check \
  tail-safe-logs \
  update-repo-map
do
  ln -sfn "$PWD/skills/$skill" "$HOME/.codex/skills/$skill"
done
```

Only the custom DGX workflow skills are vendored here. Built-in skills such as `skill-creator`, `skill-installer`, and `openai-docs` are intentionally excluded.

## License

MIT
