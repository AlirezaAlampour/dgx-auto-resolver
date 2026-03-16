#!/usr/bin/env python3
"""Backward-compatible entrypoint for dgx-auto-resolver."""

from __future__ import annotations

import sys

from resolver.resolve_deps import ResolverError, main


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ResolverError as exc:
        print(f"[resolver] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
