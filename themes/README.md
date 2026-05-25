# GhostHub Themes

This directory holds community-contributed GhostHub themes. Each `.json` file becomes a card in the gallery at `https://<your-pages-domain>/`.

## Contributing a theme

1. Fork this repo.
2. Add a new `.json` file under `themes/` — pick a unique slug for the filename, e.g. `tokyo-drift.json`.
3. Use the format below.
4. Open a pull request.

## File format

```json
{
  "name": "Tokyo Drift",
  "colors": {
    "primary": "#1f1f2e",
    "accent": "#ff3d7f",
    "background": "#0c0c14",
    "surface": "#191926",
    "text": "#f7f7ff"
  },
  "version": "1.0",
  "description": "Neon-soaked nights, drifting through cherry-pink rain.",
  "tags": ["dark", "neon", "pink"],
  "author": "your-github-handle"
}
```

### Required fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Display name in the gallery |
| `colors` | object | Must include `primary`, `accent`, `background`, `surface`, `text` as 6-digit hex |
| `version` | string | Use `"1.0"` for now |

### Optional fields (gallery-only)

These show up on the theme card but are stripped before copying to GhostHub:

| Field | Type | Notes |
|---|---|---|
| `description` | string | One-line blurb |
| `tags` | string[] | Used for filtering |
| `author` | string | GitHub handle (or anything you want next to "by") |

## How users import your theme

1. They click **Copy** on your theme card.
2. They open GhostHub → settings → theme builder → **Paste JSON**.
3. The 5 colors land in their theme builder and they can save it.

Optional metadata (`description`, `tags`, `author`) is intentionally stripped from the copy payload — GhostHub only needs `name` + `colors` + `version`.
