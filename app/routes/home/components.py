from sprag import Component, ui


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


class ThemeGallery(Component):
    def _render_swatch(self, color_value, label):
        return ui.div(
            class_="theme-card__swatch",
            style="background:" + str(color_value or "#000"),
            title=label,
        )

    def _render_card(self, theme):
        colors = theme.get("colors") or {}
        slug = theme.get("slug") or theme.get("name") or ""
        active_slug = self.state.get("active_slug") or ""
        is_active = slug == active_slug
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
                    ui.span(
                        theme.get("tags_display") or "",
                        class_="theme-card__tags",
                    ) if theme.get("tags_display") else None,
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

    def _theme_matches(self, theme, query):
        name_raw = theme.get("name") or ""
        name = name_raw.lower()
        description_raw = theme.get("description") or ""
        description = description_raw.lower()
        author_raw = theme.get("author") or ""
        author = author_raw.lower()
        if query in name or query in description or query in author:
            return True
        tags = theme.get("tags") or []
        for tag in tags:
            tag_str = str(tag).lower()
            if query in tag_str:
                return True
        return False

    def _get_filtered_themes(self):
        themes = self.state.get("themes") or []
        raw = self.state.get("search_query") or ""
        query = raw.strip().lower()
        if not query:
            return themes
        return [t for t in themes if self._theme_matches(t, query)]

    def render(self, props=None):
        all_themes = self.state.get("themes") or []
        filtered = self._get_filtered_themes()
        active_slug = self.state.get("active_slug") or ""
        active_name = self.state.get("active_name") or ""
        search_query = self.state.get("search_query") or ""
        toast = self.state.get("toast") or ""

        total = len(all_themes)
        shown = len(filtered)

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
                        "Be the first to contribute — open a PR with a JSON file in ",
                        ui.code("/themes/"),
                        " of this repo.",
                    ),
                    ui.a(
                        "How to contribute →",
                        href="https://github.com/BleedingXiko/GhosthHub_Themes#contributing-a-theme",
                        class_="gallery__cta",
                        target="_blank",
                        rel="noopener",
                    ),
                    class_="gallery__empty",
                ),
                class_="gallery",
            )

        no_results = ui.section(
            ui.h2("No matches"),
            ui.p(
                "Nothing matched ",
                ui.code(search_query),
                ". Try another name or tag.",
            ),
            ui.button(
                "Clear search",
                type="button",
                data_role="clear-search",
                class_="gallery__cta",
            ),
            class_="gallery__empty",
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
                        " to re-skin this page · ",
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
                            placeholder="Search by name, tag, author…",
                            data_role="search",
                            value=search_query,
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
                        ) if search_query else None,
                        class_="gallery__search",
                    ),
                    ui.a(
                        "Contribute →",
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
                ui.span(
                    (str(shown) + " of " + str(total) + " themes") if search_query else (str(total) + " themes"),
                    class_="gallery__count",
                ),
                ui.div(
                    ui.span("Previewing ", class_="gallery__active-label"),
                    ui.strong(active_name, class_="gallery__active-name"),
                    ui.button(
                        icon_clear(),
                        ui.span("Reset"),
                        type="button",
                        data_role="reset",
                        class_="gallery__reset",
                    ),
                    class_="gallery__active",
                ) if active_slug else None,
                class_="gallery__statusbar",
            ),
            ui.main(
                ui.Grid(
                    filtered,
                    key=lambda t: t.get("slug") or t.get("name") or "",
                    render=lambda t: self._render_card(t),
                    column_width="320px",
                    gap="1.5rem",
                ) if shown > 0 else no_results,
                class_="gallery__main",
            ),
            ui.div(
                toast,
                class_="gallery__toast",
                data_active=("true" if toast else "false"),
            ),
            class_="gallery",
            data_active_slug=active_slug,
        )
