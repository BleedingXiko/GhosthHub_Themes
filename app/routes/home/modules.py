from sprag import Module, browser

from .components import ThemeVirtualList


class ThemeGalleryModule(Module):
    def __init__(self, screen=None, state=None):
        super().__init__(
            screen=screen,
            state=state or {
                "theme_index": {"records": [], "total": 0, "pages": []},
                "initial_pages": {},
            },
        )
        self.list_component = None
        self.active_slug = ""
        self.active_name = ""
        self.toast_timer = None

    def sync_component(self, component, state):
        return None

    def on_start(self):
        slot = self.element.querySelector("[data-role='list-slot']")
        self.list_component = ThemeVirtualList(self.state, {"props": self.state})
        self.adopt_component(self.list_component, {"startArgs": [slot]})

        self.delegate(self.element, "click", "[data-role='preview']", self.on_preview)
        self.delegate(self.element, "click", "[data-role='copy']", self.on_copy)
        self.delegate(self.element, "click", "[data-role='reset']", self.on_reset)
        self.delegate(self.element, "click", "[data-role='clear-search']", self.on_clear_search)
        self.delegate(self.element, "input", "[data-role='search']", self.on_search)
        self._sync_status("")

    def on_preview(self, event, target):
        event.prevent_default()
        slug = target.dataset.slug
        theme = self.list_component.find_theme(slug)
        if not theme:
            return None
        colors = theme.get("colors") or {}
        self._apply_vars(
            colors.get("primary") or "",
            colors.get("accent") or "",
            colors.get("background") or "",
            colors.get("surface") or "",
            colors.get("text") or "",
        )
        self.active_slug = slug
        self.active_name = theme.get("name") or ""
        self.list_component.set_active(self.active_slug, self.active_name)
        self._sync_status(self._search_value())

    def on_copy(self, event, target):
        event.prevent_default()
        slug = target.dataset.slug
        theme = self.list_component.find_theme(slug)
        if not theme:
            return None
        payload = {
            "name": theme.get("name") or "",
            "colors": theme.get("colors") or {},
            "version": theme.get("version") or "1.0",
        }
        text = browser.JSON.stringify(payload, None, 2)
        browser.navigator.clipboard.writeText(text)
        name = theme.get("name") or ""
        self._set_toast("Copied \"" + name + "\" to clipboard")

    def on_reset(self, event, target):
        event.prevent_default()
        self._apply_vars("#2d3250", "#f05454", "#121212", "#1e1e2e", "#ffffff")
        self.active_slug = ""
        self.active_name = ""
        self.list_component.set_active("", "")
        self._sync_status(self._search_value())

    def on_search(self, event, target):
        query = target.value or ""
        self.list_component.set_query(query)
        self._sync_status(query)

    def on_clear_search(self, event, target):
        event.prevent_default()
        input_el = self.element.querySelector("[data-role='search']")
        if input_el:
            input_el.value = ""
            input_el.focus()
        self.list_component.set_query("")
        self._sync_status("")

    def _search_value(self):
        input_el = self.element.querySelector("[data-role='search']")
        if input_el:
            return input_el.value or ""
        return ""

    def _apply_vars(self, primary, accent, background, surface, text):
        root = browser.document.documentElement
        root.style.setProperty("--primary-color", primary)
        root.style.setProperty("--accent-color", accent)
        root.style.setProperty("--background-color", background)
        root.style.setProperty("--surface-color", surface)
        root.style.setProperty("--text-primary", text)

    def _sync_status(self, query):
        shown = self.list_component.visible_count()
        total = self.list_component.total_count()
        count = self.element.querySelector("[data-role='count']")
        if count:
            if query:
                count.textContent = str(shown) + " of " + str(total) + " themes"
            else:
                count.textContent = str(total) + " themes"

        gallery = self.element.querySelector(".gallery")
        if gallery:
            gallery.dataset.empty = "true" if shown == 0 else "false"

        active = self.element.querySelector("[data-role='active-status']")
        active_name = self.element.querySelector("[data-role='active-name']")
        if active:
            active.hidden = not bool(self.active_slug)
        if active_name:
            active_name.textContent = self.active_name

        empty_query = self.element.querySelector("[data-role='empty-query']")
        if empty_query:
            empty_query.textContent = query

        clear_buttons = self.element.querySelectorAll("[data-role='clear-search']")
        for button in clear_buttons:
            if button.classList.contains("gallery__search-clear"):
                button.hidden = not bool(query)

    def _set_toast(self, message):
        if self.toast_timer:
            self.clear_timeout(self.toast_timer)
            self.toast_timer = None
        toast = self.element.querySelector("[data-role='toast']")
        if toast:
            toast.textContent = message
            toast.dataset.active = "true" if message else "false"
        if message:
            self.toast_timer = self.timeout(self._clear_toast, 2.0)

    def _clear_toast(self):
        self._set_toast("")
