# dgx-auto-resolver

`dgx-auto-resolver` is a small Python utility for AI environments where the GPU software stack is already correct, but the application still crashes on missing Python imports.

It is designed for systems like NVIDIA DGX Spark, DGX Station, and vendor-tuned CUDA containers where reinstalling or upgrading `torch` and `torchvision` can easily destabilize a working setup.

## Why this exists

Specialized AI hardware images often ship with a carefully matched combination of:

- NVIDIA drivers
- CUDA libraries
- PyTorch wheels
- torchvision builds
- low-level acceleration plugins

In those environments, a normal `pip install -r requirements.txt` can be risky. One unpinned dependency may trigger a surprise upgrade or replacement of the exact PyTorch build that makes the hardware usable.

`dgx-auto-resolver` takes a narrower, safer approach:

1. It probes the currently installed `torch` and `torchvision` versions.
2. It writes those exact versions into `constraints.txt`.
3. It launches your target Python script.
4. If startup fails with `ModuleNotFoundError`, it installs only the missing package with `pip install --constraint constraints.txt ...`.
5. It repeats until the script boots cleanly.
6. It freezes the resulting environment to `safe_requirements.txt`.

The goal is not to be a full dependency solver. The goal is to preserve a fragile accelerator stack while filling in missing user-space Python packages one import at a time.

## Safety model

- The resolver refuses to auto-install packages that look tied to the GPU stack, such as `torch`, `torchvision`, `torchaudio`, `triton`, `xformers`, `nvidia`, or `cuda`.
- It stops immediately on errors that are not `ModuleNotFoundError`.
- It includes a small alias table for common import-name-to-package-name mismatches like `yaml -> PyYAML` and `cv2 -> opencv-python-headless`.
- It treats a process that stays alive past the startup timeout as a clean boot, stops that probe process, and then freezes the environment snapshot.

If your application depends on a package with a non-obvious distribution name, extend the `MODULE_TO_PACKAGE` mapping in `resolve_deps.py`.

## Usage

Run the resolver from the environment you want to repair:

```bash
python resolve_deps.py path/to/app.py
```

Pass arguments through to the target script:

```bash
python resolve_deps.py path/to/app.py -- --model /models/foo --port 8080
```

Useful flags:

- `--boot-timeout 10`: treat the app as healthy if it survives for 10 seconds, then stop the probe process
- `--cwd /workspace/app`: run the target script from a specific working directory
- `--constraints constraints.txt`: choose where the protected constraints file is written
- `--requirements safe_requirements.txt`: choose where the frozen environment snapshot is written
- `--verbose`: print captured stdout/stderr for retry attempts

By default, `constraints.txt` and `safe_requirements.txt` are written to the current working directory.

## Docker workflow

This tool is especially useful when you start from a known-good NVIDIA base image and want to fill in only the missing Python dependencies.

Example Dockerfile:

```dockerfile
FROM nvcr.io/nvidia/pytorch:24.02-py3

WORKDIR /workspace

COPY dgx-auto-resolver/ /opt/dgx-auto-resolver/
COPY app/ /workspace/

RUN python /opt/dgx-auto-resolver/resolve_deps.py \
    --cwd /workspace \
    --boot-timeout 8 \
    app.py

CMD ["python", "app.py"]
```

Example interactive container workflow:

```bash
docker run --rm -it --gpus all \
  -v "$PWD:/workspace" \
  -w /workspace \
  nvcr.io/nvidia/pytorch:24.02-py3 \
  python /workspace/dgx-auto-resolver/resolve_deps.py --boot-timeout 8 app.py
```

After a successful run, capture the generated `safe_requirements.txt` and use it as the reproducible snapshot for later image builds or CI jobs.

## Outputs

- `constraints.txt`: exact `torch` and `torchvision` pins used to protect the accelerator stack during installs
- `safe_requirements.txt`: `pip freeze --exclude-editable` snapshot after the application boots cleanly

## License

MIT
