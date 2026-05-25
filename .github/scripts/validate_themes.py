#!/usr/bin/env python3
"""Validate every JSON file under themes/.

Runs in CI on every PR. Standalone — no sprag dependency, so it boots fast.
Mirrors the server-side filter in app/routes/home/server.py: themes that
fail any check here would be silently dropped by the gallery, so we reject
the PR instead.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = REPO_ROOT / "themes"
REQUIRED_COLOR_KEYS = ("primary", "accent", "background", "surface", "text")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


def validate(path: Path) -> list[str]:
    errs: list[str] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"could not read: {e}"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    if not isinstance(data, dict):
        return ["top-level value must be a JSON object"]

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        errs.append("missing or empty `name` (must be a non-empty string)")

    version = data.get("version")
    if version is not None and not isinstance(version, (str, int, float)):
        errs.append("`version` must be a string")

    colors = data.get("colors")
    if not isinstance(colors, dict):
        errs.append("missing `colors` object")
    else:
        for key in REQUIRED_COLOR_KEYS:
            value = colors.get(key)
            if not isinstance(value, str):
                errs.append(f"`colors.{key}` is missing or not a string")
                continue
            if not HEX_RE.match(value):
                errs.append(
                    f"`colors.{key}` = {value!r} is not a 6- or 8-digit hex (#rrggbb or #rrggbbaa)"
                )
        extras = set(colors.keys()) - set(REQUIRED_COLOR_KEYS)
        if extras:
            errs.append(
                f"unknown keys in `colors`: {sorted(extras)} — only "
                f"{list(REQUIRED_COLOR_KEYS)} are used"
            )

    tags = data.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            errs.append("`tags` must be a list of strings")
        else:
            for i, tag in enumerate(tags):
                if not isinstance(tag, (str, int)):
                    errs.append(f"`tags[{i}]` must be a string")

    for opt in ("description", "author"):
        v = data.get(opt)
        if v is not None and not isinstance(v, str):
            errs.append(f"`{opt}` must be a string if present")

    return errs


def main() -> int:
    if not THEMES_DIR.is_dir():
        print(f"::error::{THEMES_DIR} does not exist")
        return 1

    paths = sorted(THEMES_DIR.glob("*.json"))
    if not paths:
        print(f"::warning::no theme files found in {THEMES_DIR}")
        return 0

    seen_slugs: dict[str, Path] = {}
    seen_names: dict[str, Path] = {}
    failed = 0

    for path in paths:
        rel = path.relative_to(REPO_ROOT)
        errs = validate(path)
        slug = path.stem
        if slug in seen_slugs:
            errs.append(f"duplicate slug `{slug}` (also in {seen_slugs[slug].name})")
        else:
            seen_slugs[slug] = path
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            name = (data.get("name") or "").strip().lower()
            if name:
                if name in seen_names:
                    errs.append(
                        f"duplicate display name {data.get('name')!r} (also in {seen_names[name].name})"
                    )
                else:
                    seen_names[name] = path
        except Exception:
            pass

        if errs:
            failed += 1
            print(f"::error file={rel}::{rel} has {len(errs)} problem(s):")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"ok  {rel}")

    print()
    print(f"checked {len(paths)} file(s), {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
