# GhostHub Themes

A community theme gallery for [GhostHub](https://github.com/BleedingXiko/GhostHub) — browse, preview, and copy themes built by the community, then paste them into GhostHub's theme builder.

The site is a static SPRAG app deployed to GitHub Pages. Every `.json` file in `themes/` becomes a card in the gallery.

## Try a theme

1. Open the gallery: https://bleedingxiko.github.io/GhostHub_Themes/
2. Click **Preview** on any card — the whole page re-skins so you can see it live.
3. Click **Copy** to put the GhostHub-importable JSON on your clipboard.
4. In GhostHub: settings → theme builder → **Paste JSON** → save.

## Contribute a theme

Full format spec lives in [`themes/README.md`](themes/README.md). The short version:

1. Fork this repo.
2. Add a JSON file under `themes/`, e.g. `themes/your-theme-name.json`:

   ```json
   {
     "name": "Your Theme",
     "colors": {
       "primary":    "#1f1f2e",
       "accent":     "#ff3d7f",
       "background": "#0c0c14",
       "surface":    "#191926",
       "text":       "#f7f7ff"
     },
     "version": "1.0",
     "description": "Optional one-liner.",
     "tags": ["dark", "neon"],
     "author": "your-github-handle"
   }
   ```

3. Open a PR. CI validates the JSON. Once merged, your theme is live on the gallery within a minute.

`description`, `tags`, and `author` are gallery-only — they're stripped before the **Copy** button writes anything to your clipboard, so GhostHub only ever sees `name`, `colors`, `version`.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
sprag dev static
```

Open the URL printed in the terminal.

## Build a static bundle

```bash
python .github/scripts/build_theme_index.py
sprag build static
```

Output lands in `dist/`.

## Project layout

```
GhostHub_Themes/
├── app/                  # SPRAG app (gallery UI)
│   ├── routes/home/      # the single page
│   ├── shell.html        # body fragment + slot
│   ├── shell.css         # base CSS vars (driven by --primary/--accent/etc)
│   └── __init__.py
├── themes/               # ← contribute here
│   ├── README.md         # format spec
│   └── *.json
├── .github/
│   ├── workflows/        # CI: validate + deploy
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── requirements.txt
├── LICENSE
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).
