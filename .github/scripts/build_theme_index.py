#!/usr/bin/env python3
"""Generate the static theme manifest and page chunks used by the gallery."""
from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from app.theme_data import write_static_theme_catalog


def main() -> int:
    index = write_static_theme_catalog()
    pages = len(index.get("pages") or [])
    total = index.get("total", 0)
    print(f"wrote static theme index: {total} theme(s), {pages} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
