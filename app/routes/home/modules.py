from sprag import Module, browser


class ThemeGalleryModule(Module):
    def __init__(self, screen=None, state=None):
        super().__init__(
            screen=screen,
            state=state or {
                "themes": [],
                "active_slug": "",
                "active_name": "",
                "toast": "",
                "search_query": "",
            },
        )

    def on_start(self):
        self.delegate(self.element, "click", "[data-role='preview']", self._on_preview)
        self.delegate(self.element, "click", "[data-role='copy']", self._on_copy)
        self.delegate(self.element, "click", "[data-role='reset']", self._on_reset)
        self.delegate(self.element, "click", "[data-role='clear-search']", self._on_clear_search)
        self.delegate(self.element, "input", "[data-role='search']", self._on_search)

    def _find_theme(self, slug):
        themes = self.state.get("themes") or []
        for theme in themes:
            if theme.get("slug") == slug:
                return theme
        return None

    def _apply_vars(self, primary, accent, background, surface, text):
        root = browser.document.documentElement
        root.style.setProperty("--primary-color", primary)
        root.style.setProperty("--accent-color", accent)
        root.style.setProperty("--background-color", background)
        root.style.setProperty("--surface-color", surface)
        root.style.setProperty("--text-primary", text)

    def _on_preview(self, event, target):
        event.prevent_default()
        slug = target.dataset.slug
        theme = self._find_theme(slug)
        if not theme:
            return None
        colors = theme.get("colors") or {}
        primary = colors.get("primary") or ""
        accent = colors.get("accent") or ""
        background = colors.get("background") or ""
        surface = colors.get("surface") or ""
        text = colors.get("text") or ""
        self._apply_vars(primary, accent, background, surface, text)
        name = theme.get("name") or ""
        self.set_state({"active_slug": slug, "active_name": name})

    def _on_reset(self, event, target):
        event.prevent_default()
        self._apply_vars("#2d3250", "#f05454", "#121212", "#1e1e2e", "#ffffff")
        self.set_state({"active_slug": "", "active_name": ""})

    def _on_copy(self, event, target):
        event.prevent_default()
        slug = target.dataset.slug
        theme = self._find_theme(slug)
        if not theme:
            return None
        payload = {
            "name": theme.get("name") or "",
            "colors": theme.get("colors") or {},
            "version": theme.get("version") or "1.0",
        }
        text = browser.JSON.stringify(payload, None, 2)
        browser.navigator.clipboard.writeText(text)
        self.set_state({"toast": "Copied “" + (theme.get("name") or "") + "” to clipboard"})
        self.timeout(self._clear_toast, 2.0)

    def _clear_toast(self):
        self.set_state({"toast": ""})

    def _on_search(self, event, target):
        self.set_state({"search_query": target.value or ""})

    def _on_clear_search(self, event, target):
        event.prevent_default()
        self.set_state({"search_query": ""})
        input_el = self.element.querySelector("[data-role='search']")
        if input_el:
            input_el.value = ""
            input_el.focus()
