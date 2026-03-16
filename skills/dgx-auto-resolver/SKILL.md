---
name: dgx-auto-resolver
description: Safely repair Dockerized Python applications on DGX, DGX Spark, DGX Station, and similar Blackwell/CUDA environments when startup fails with ModuleNotFoundError or a pure Python ImportError caused by missing packages. Use when Codex must inject the bundled resolver script, wait for safe_requirements.txt to be generated from the real container workflow, and rewrite the Dockerfile without replacing the vendor-tuned ARM64 PyTorch or torchvision stack.
---

# DGX Auto Resolver

Use this skill to recover missing Python imports inside a container while preserving the base image's GPU stack.

## Guardrails

- Confirm the failure is `ModuleNotFoundError` or a package-level `ImportError` caused by a missing Python distribution.
- Stop and escalate if the traceback points to ABI, shared-library, CUDA, or wheel-compatibility problems such as `undefined symbol`, `.so` load failures, `GLIBC`, `libopenblas`, `libcudart`, or missing vendor GPU wheels.
- Treat `ImportError: cannot import name ...` as a possible version mismatch, not an automatic dependency-install case, unless the traceback clearly shows a missing package.
- Never upgrade, uninstall, or replace `torch`, `torchvision`, `torchaudio`, `triton`, `xformers`, `nvidia*`, `cuda*`, or similar accelerator packages unless the user explicitly asks.

## Workflow

### 1. Identify the real failing entrypoint

- Inspect `Dockerfile`, `docker-compose.yml`, startup scripts, and app docs to find the Python command that actually crashes.
- Reuse the existing base image, `WORKDIR`, and startup command whenever possible.
- Prefer fixing the container workflow the project already uses instead of inventing a parallel launcher.

### 2. Inject the bundled resolver

- Use `assets/resolve_deps.py` as the canonical resolver script.
- Copy it into the target repo or image instead of rewriting it from scratch unless the task requires a local customization.
- Place it somewhere explicit such as `tools/resolve_deps.py` in the repo or `/opt/dgx-auto-resolver/resolve_deps.py` in the image.

### 3. Generate `safe_requirements.txt`

- Patch the Dockerfile so it copies the resolver and runs it against the real app entrypoint during build or in a one-off container run.
- Keep going until `safe_requirements.txt` actually exists. Do not stop after only editing files.
- If the app depends on runtime-only volumes, secrets, or mounted model data, use an interactive container workflow instead of forcing a broken `docker build`.

Example bootstrap pattern:

```dockerfile
COPY tools/resolve_deps.py /opt/dgx-auto-resolver/resolve_deps.py
RUN python /opt/dgx-auto-resolver/resolve_deps.py \
    --cwd /workspace \
    --boot-timeout 8 \
    app.py -- --host 0.0.0.0
```

### 4. Rewrite the Dockerfile after the snapshot exists

- Replace the one-off bootstrap step with a reproducible install path after `safe_requirements.txt` has been generated.
- Copy `safe_requirements.txt` into the build context and install only the user-space packages needed by the app.
- Filter out protected accelerator packages before installation so the base image keeps its vendor-tuned PyTorch bindings.
- Create a derived file such as `app_requirements.txt` during the build instead of hand-editing `safe_requirements.txt`.

Safe install pattern:

```dockerfile
COPY safe_requirements.txt /tmp/safe_requirements.txt
RUN python - <<'PY'
from pathlib import Path

protected_prefixes = (
    "torch==",
    "torchvision==",
    "torchaudio==",
    "triton==",
    "xformers==",
    "nvidia-",
    "cuda",
    "cudnn",
)

src = Path("/tmp/safe_requirements.txt")
dst = Path("/tmp/app_requirements.txt")
lines = [
    line
    for line in src.read_text(encoding="utf-8").splitlines()
    if line and not line.startswith("#") and not line.startswith(protected_prefixes)
]
dst.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
PY
RUN python -m pip install --disable-pip-version-check --upgrade-strategy only-if-needed -r /tmp/app_requirements.txt
```

### 5. Validate the repaired image

- Rebuild the image or rerun the container and confirm the app reaches a clean startup.
- Verify `safe_requirements.txt` was generated from the working environment, not guessed.
- Review the final diff to ensure the Dockerfile change preserves the original base image and does not add broad `pip install -U` or `pip install -r requirements.txt` steps.

## Asset

- `assets/resolve_deps.py`: Canonical dependency resolver that pins the existing `torch` and `torchvision` versions as install constraints, installs missing packages one at a time, and freezes the resulting environment to `safe_requirements.txt`.
