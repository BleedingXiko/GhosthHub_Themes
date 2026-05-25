import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
THEMES_DIR = REPO_ROOT / "themes"
STATIC_THEME_DATA_DIR = REPO_ROOT / "app" / "static" / "theme-data"
REQUIRED_COLOR_KEYS = ("primary", "accent", "background", "surface", "text")
DEFAULT_PAGE_SIZE = 96


def load_themes():
    themes = []
    if not THEMES_DIR.is_dir():
        return themes
    for path in sorted(THEMES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        colors = data.get("colors")
        if not isinstance(colors, dict):
            continue
        if not all(isinstance(colors.get(k), str) for k in REQUIRED_COLOR_KEYS):
            continue
        tags = [str(t) for t in (data.get("tags") or []) if isinstance(t, (str, int))]
        themes.append({
            "slug": path.stem,
            "name": str(data.get("name") or path.stem),
            "colors": {k: colors[k] for k in REQUIRED_COLOR_KEYS},
            "version": str(data.get("version") or "1.0"),
            "description": data.get("description") or "",
            "tags": tags,
            "tags_display": " · ".join(tags),
            "author": data.get("author") or "",
        })
    return themes


def build_theme_catalog(page_size=DEFAULT_PAGE_SIZE):
    themes = load_themes()
    records = []
    pages = []

    for page_index, start in enumerate(range(0, len(themes), page_size)):
        page_themes = themes[start:start + page_size]
        page_name = str(page_index).zfill(4) + ".json"
        pages.append({
            "index": page_index,
            "count": len(page_themes),
            "url": "pages/" + page_name,
        })
        for offset, theme in enumerate(page_themes):
            searchable = " ".join([
                theme.get("name") or "",
                theme.get("description") or "",
                theme.get("author") or "",
                " ".join(theme.get("tags") or []),
            ]).lower()
            records.append({
                "slug": theme["slug"],
                "name": theme["name"],
                "description": theme.get("description") or "",
                "tags": theme.get("tags") or [],
                "tags_display": theme.get("tags_display") or "",
                "author": theme.get("author") or "",
                "page": page_index,
                "offset": offset,
                "search": searchable,
            })

    return {
        "version": 1,
        "page_size": page_size,
        "total": len(themes),
        "pages": pages,
        "records": records,
    }, themes


def write_static_theme_catalog(output_dir=STATIC_THEME_DATA_DIR, page_size=DEFAULT_PAGE_SIZE):
    index, themes = build_theme_catalog(page_size=page_size)
    output_dir = Path(output_dir)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    for old_page in pages_dir.glob("*.json"):
        old_page.unlink()

    for page in index["pages"]:
        start = page["index"] * page_size
        page_themes = themes[start:start + page_size]
        page_path = output_dir / page["url"]
        page_path.write_text(
            json.dumps({"themes": page_themes}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    (output_dir / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return index
