from sprag import Component, browser, join_url, ui, virtual_scroll


SCROLL_CHUNK_SIZE = 24
INITIAL_SCROLL_CHUNKS = 2


def _icon_svg(*children):
    return ui.svg(
        *children,
        viewBox="0 0 24 24",
        fill="none",
        stroke="currentColor",
        class_="icon",
        aria_hidden="true",
    )


def icon_search():
    return _icon_svg(
        ui.circle(cx="11", cy="11", r="7"),
        ui.path(d="m20 20-3.5-3.5"),
    )


def icon_clear():
    return _icon_svg(
        ui.path(d="M18 6 6 18"),
        ui.path(d="m6 6 12 12"),
    )


def icon_copy():
    return _icon_svg(
        ui.rect(width="14", height="14", x="8", y="8", rx="2"),
        ui.path(d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"),
    )


def icon_eye():
    return _icon_svg(
        ui.path(d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"),
        ui.circle(cx="12", cy="12", r="3"),
    )


class ThemeGalleryShell(Component):
    def _data(self, props=None):
        return props or self.props or self.state or {}

    def _index(self, props=None):
        data = self._data(props)
        return data.get("theme_index") or {"records": [], "total": 0, "pages": []}

    def _empty_state(self):
        return ui.section(
            ui.h2("No matches"),
            ui.p(
                "Nothing matched ",
                ui.code("", data_role="empty-query"),
                ". Try another name or tag.",
            ),
            ui.button(
                "Clear search",
                type="button",
                data_role="clear-search",
                class_="gallery__cta",
            ),
            class_="gallery__empty gallery__empty--search",
        )

    def render(self, props=None):
        index = self._index(props)
        total = index.get("total") or 0

        if total == 0:
            return ui.div(
                ui.header(
                    ui.div(
                        ui.span("ghosthub /", class_="gallery__brand-mark"),
                        ui.h1("Themes", class_="gallery__brand-title"),
                        class_="gallery__brand",
                    ),
                    class_="gallery__header",
                ),
                ui.section(
                    ui.h2("No themes yet"),
                    ui.p(
                        "Be the first to contribute - open a PR with a JSON file in ",
                        ui.code("/themes/"),
                        " of this repo.",
                    ),
                    ui.a(
                        "How to contribute ->",
                        href="https://github.com/BleedingXiko/GhosthHub_Themes#contributing-a-theme",
                        class_="gallery__cta",
                        target="_blank",
                        rel="noopener",
                    ),
                    class_="gallery__empty",
                ),
                class_="gallery",
                data_empty="true",
            )

        return ui.div(
            ui.header(
                ui.div(
                    ui.div(
                        ui.span("ghosthub /", class_="gallery__brand-mark"),
                        ui.h1("Themes", class_="gallery__brand-title"),
                        class_="gallery__brand",
                    ),
                    ui.p(
                        "Click ",
                        ui.strong("Preview"),
                        " to re-skin this page - ",
                        ui.strong("Copy"),
                        " to paste into GhostHub's theme builder.",
                        class_="gallery__lede",
                    ),
                    class_="gallery__intro",
                ),
                ui.div(
                    ui.div(
                        icon_search(),
                        ui.input(
                            type="search",
                            placeholder="Search by name, tag, author...",
                            data_role="search",
                            class_="gallery__search-input",
                            aria_label="Search themes",
                            autocomplete="off",
                            spellcheck="false",
                        ),
                        ui.button(
                            icon_clear(),
                            type="button",
                            data_role="clear-search",
                            class_="gallery__search-clear",
                            aria_label="Clear search",
                            hidden=True,
                        ),
                        class_="gallery__search",
                    ),
                    ui.a(
                        "Contribute ->",
                        href="https://github.com/BleedingXiko/GhosthHub_Themes#contributing-a-theme",
                        class_="gallery__cta",
                        target="_blank",
                        rel="noopener",
                    ),
                    class_="gallery__controls",
                ),
                class_="gallery__header",
            ),
            ui.div(
                ui.span(str(total) + " themes", class_="gallery__count", data_role="count"),
                ui.div(
                    ui.span("Previewing ", class_="gallery__active-label"),
                    ui.strong("", class_="gallery__active-name", data_role="active-name"),
                    ui.button(
                        icon_clear(),
                        ui.span("Reset"),
                        type="button",
                        data_role="reset",
                        class_="gallery__reset",
                    ),
                    class_="gallery__active",
                    data_role="active-status",
                    hidden=True,
                ),
                class_="gallery__statusbar",
            ),
            self._empty_state(),
            ui.div(class_="gallery__list-slot", data_role="list-slot"),
            ui.div("", class_="gallery__toast", data_role="toast", data_active="false"),
            class_="gallery",
            data_empty="false",
        )


@virtual_scroll(
    chunk=SCROLL_CHUNK_SIZE,
    max_chunks=6,
    initial_chunks=INITIAL_SCROLL_CHUNKS,
    container_class="gallery__virtual-scroller",
)
class ThemeVirtualList(Component):
    def _data(self, props=None):
        return props or self.props or self.state or {}

    def _index(self, props=None):
        data = self._data(props)
        return data.get("theme_index") or {"records": [], "total": 0, "pages": []}

    def _initial_pages(self, props=None):
        data = self._data(props)
        return data.get("initial_pages") or {}

    def _ensure_ready(self):
        if self._ready:
            return None
        index = self._index()
        self._records = index.get("records") or []
        self._filtered_records = self._records
        self._pages = self._initial_pages()
        self._loading_pages = {}
        self._failed_pages = {}
        self._search_query = ""
        self._active_slug = ""
        self._active_name = ""
        self._ready = True
        return None

    def on_start(self):
        self._ensure_ready()
        self._ensure_range(0, SCROLL_CHUNK_SIZE * INITIAL_SCROLL_CHUNKS)
        self.virtual_scroll.reset()

    def render(self, props=None):
        return ui.div(class_="theme-list")

    def _page_key(self, page):
        return str(page)

    def _theme_data_url(self, url):
        return join_url("/static", "theme-data", url)

    def _page_url(self, page):
        key = self._page_key(page)
        if page < 10:
            return "pages/000" + key + ".json"
        if page < 100:
            return "pages/00" + key + ".json"
        if page < 1000:
            return "pages/0" + key + ".json"
        return "pages/" + key + ".json"

    async def _fetch_page(self, page):
        key = self._page_key(page)
        try:
            response = await browser.fetch(self._theme_data_url(self._page_url(page)))
            data = await response.json()
            self._pages = browser.Object.assign({}, self._pages, {key: data.get("themes") or []})
            self._failed_pages = browser.Object.assign({}, self._failed_pages, {key: False})
        except Exception:
            self._failed_pages = browser.Object.assign({}, self._failed_pages, {key: True})
        self._loading_pages = browser.Object.assign({}, self._loading_pages, {key: False})
        self.virtual_scroll.reset()

    def _ensure_page(self, page):
        key = self._page_key(page)
        pages = self._current_pages()
        if pages.get(key):
            return None
        loading_pages = self._current_loading_pages()
        if loading_pages.get(key):
            return None
        self._loading_pages = browser.Object.assign({}, self._loading_pages, {key: True})
        self._fetch_page(page)
        return None

    def _ensure_range(self, start, end):
        records = self._current_records()
        stop = min(end, len(records))
        for i in range(start, stop):
            record = records[i]
            self._ensure_page(record.get("page") or 0)

    def _current_records(self):
        records = self._filtered_records
        if records:
            return records
        if self._search_query:
            return []
        return self._index().get("records") or []

    def _current_pages(self):
        return self._pages or self._initial_pages()

    def _current_loading_pages(self):
        return self._loading_pages or {}

    def _theme_for_record(self, record):
        page = self._current_pages().get(self._page_key(record.get("page") or 0))
        if not page:
            return None
        offset = record.get("offset") or 0
        if offset >= len(page):
            return None
        return page[offset]

    def find_theme(self, slug):
        self._ensure_ready()
        for page in browser.Object.values(self._current_pages()):
            for theme in page:
                if theme.get("slug") == slug:
                    return theme
        return None

    def _theme_matches(self, record, query):
        search_text = record.get("search") or ""
        return search_text.indexOf(query) >= 0

    def set_query(self, query):
        self._ensure_ready()
        value = query or ""
        self._search_query = value.strip().lower()
        if not self._search_query:
            self._filtered_records = self._records
        else:
            self._filtered_records = [r for r in self._records if self._theme_matches(r, self._search_query)]
        self._ensure_range(0, SCROLL_CHUNK_SIZE * INITIAL_SCROLL_CHUNKS)
        self.virtual_scroll.recycle()
        self.virtual_scroll.rebind({}, self.element)
        self._set_active_card_dom(self._active_slug)

    def visible_count(self):
        self._ensure_ready()
        return len(self._current_records())

    def total_count(self):
        self._ensure_ready()
        return len(self._records)

    def set_active(self, slug, name):
        self._ensure_ready()
        self._active_slug = slug or ""
        self._active_name = name or ""
        self._set_active_card_dom(self._active_slug)

    def _set_active_card_dom(self, slug):
        cards = self.element.querySelectorAll("[data-role='theme-card']")
        for card in cards:
            is_active = card.dataset.slug == slug
            card.classList.toggle("is-active", is_active)
            button = card.querySelector("[data-role='preview']")
            if button:
                button.classList.toggle("is-active", is_active)
                label = button.querySelector("span")
                if label:
                    label.textContent = "Active" if is_active else "Preview"

    def _render_swatch(self, color_value, label):
        return ui.div(
            class_="theme-card__swatch",
            style="background:" + str(color_value or "#000"),
            title=label,
        )

    def _render_loading_card(self, record):
        return ui.article(
            ui.div(
                ui.div(class_="theme-card__skeleton-swatch"),
                ui.div(class_="theme-card__skeleton-swatch"),
                ui.div(class_="theme-card__skeleton-swatch"),
                ui.div(class_="theme-card__skeleton-swatch"),
                ui.div(class_="theme-card__skeleton-swatch"),
                class_="theme-card__swatches",
            ),
            ui.header(
                ui.h3(record.get("name") or "Loading theme", class_="theme-card__name"),
                ui.p("Loading theme data...", class_="theme-card__desc"),
                class_="theme-card__header",
            ),
            class_="theme-card theme-card--loading",
            data_role="theme-card",
            data_slug=record.get("slug") or "",
        )

    def _render_card(self, theme):
        colors = theme.get("colors") or {}
        slug = theme.get("slug") or theme.get("name") or ""
        is_active = slug == self._active_slug
        return ui.article(
            ui.div(
                self._render_swatch(colors.get("primary"), "Primary"),
                self._render_swatch(colors.get("accent"), "Accent"),
                self._render_swatch(colors.get("background"), "Background"),
                self._render_swatch(colors.get("surface"), "Surface"),
                self._render_swatch(colors.get("text"), "Text"),
                class_="theme-card__swatches",
            ),
            ui.header(
                ui.h3(theme.get("name") or "Untitled", class_="theme-card__name"),
                ui.p(theme.get("description") or "", class_="theme-card__desc")
                    if theme.get("description") else None,
                class_="theme-card__header",
            ),
            ui.footer(
                ui.div(
                    ui.span("by " + (theme.get("author") or ""), class_="theme-card__author")
                        if theme.get("author") else None,
                    ui.span(theme.get("tags_display") or "", class_="theme-card__tags")
                        if theme.get("tags_display") else None,
                    class_="theme-card__meta",
                ),
                ui.div(
                    ui.button(
                        icon_eye(),
                        ui.span("Active" if is_active else "Preview"),
                        type="button",
                        data_role="preview",
                        data_slug=slug,
                        class_=("theme-card__btn theme-card__btn--ghost is-active" if is_active else "theme-card__btn theme-card__btn--ghost"),
                    ),
                    ui.button(
                        icon_copy(),
                        ui.span("Copy"),
                        type="button",
                        data_role="copy",
                        data_slug=slug,
                        class_="theme-card__btn theme-card__btn--primary",
                    ),
                    class_="theme-card__actions",
                ),
                class_="theme-card__footer",
            ),
            class_=("theme-card is-active" if is_active else "theme-card"),
            data_role="theme-card",
            data_slug=slug,
        )

    def _render_record_card(self, record):
        theme = self._theme_for_record(record)
        if theme:
            return self._render_card(theme)
        return self._render_loading_card(record)

    def total(self):
        self._ensure_ready()
        return len(self._current_records())

    def chunk(self, i):
        self._ensure_ready()
        start = i * SCROLL_CHUNK_SIZE
        stop = min(start + SCROLL_CHUNK_SIZE, self.total())
        self._ensure_range(start, stop)
        cards = [
            self._render_record_card(self._current_records()[index])
            for index in range(start, stop)
        ]
        return ui.div(cards, class_="gallery__virtual-chunk")
