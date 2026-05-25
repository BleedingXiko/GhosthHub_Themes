import json
from pathlib import Path

from sprag import Controller


THEMES_DIR = Path(__file__).resolve().parents[3] / "themes"
REQUIRED_COLOR_KEYS = ("primary", "accent", "background", "surface", "text")


def _load_themes():
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


class HomeController(Controller):
    route = "/"

    def load(self):
        return {"themes": _load_themes()}
