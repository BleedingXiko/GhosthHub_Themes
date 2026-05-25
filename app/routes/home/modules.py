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
        self.delegate(self.element, "click", "[data-role='tag']", self.on_tag_click)
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

    def on_tag_click(self, event, target):
        event.prevent_default()
        tag = target.dataset.tag or ""
        input_el = self.element.querySelector("[data-role='search']")
        if input_el:
            input_el.value = tag
            input_el.focus()
        self.list_component.set_query(tag)
        self._sync_status(tag)

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

    def _hex_to_rgb(self, hex_val):
        hex_clean = hex_val.substring(1) if hex_val.startsWith('#') else hex_val
        # Standardize 3-character hex to 6-character flatly
        hex_six = (hex_clean.substring(0, 1) + hex_clean.substring(0, 1) + 
                   hex_clean.substring(1, 2) + hex_clean.substring(1, 2) + 
                   hex_clean.substring(2, 3) + hex_clean.substring(2, 3)) if len(hex_clean) == 3 else hex_clean
        
        r_str = hex_six.substring(0, 2)
        g_str = hex_six.substring(2, 4)
        b_str = hex_six.substring(4, 6)
        return [
            browser.parseInt(r_str, 16),
            browser.parseInt(g_str, 16),
            browser.parseInt(b_str, 16)
        ]

    def _rgb_to_hex(self, r, g, b):
        r_round = browser.Math.max(0, browser.Math.min(255, browser.Math.round(r)))
        g_round = browser.Math.max(0, browser.Math.min(255, browser.Math.round(g)))
        b_round = browser.Math.max(0, browser.Math.min(255, browser.Math.round(b)))
        
        r_hex = r_round.toString(16)
        g_hex = g_round.toString(16)
        b_hex = b_round.toString(16)
        
        r_hex_padded = "0" + r_hex if len(r_hex) == 1 else r_hex
        g_hex_padded = "0" + g_hex if len(g_hex) == 1 else g_hex
        b_hex_padded = "0" + b_hex if len(b_hex) == 1 else b_hex
            
        return "#" + r_hex_padded + g_hex_padded + b_hex_padded

    def _hex_to_hsl(self, hex_val):
        rgb = self._hex_to_rgb(hex_val)
        r = rgb[0] / 255.0
        g = rgb[1] / 255.0
        b = rgb[2] / 255.0
        
        max_val = browser.Math.max(r, g, b)
        min_val = browser.Math.min(r, g, b)
        
        l_val = (max_val + min_val) / 2.0
        
        if max_val == min_val:
            return [0.0, 0.0, l_val * 100.0]
            
        d = max_val - min_val
        s_val = d / (2.0 - max_val - min_val) if l_val > 0.5 else d / (max_val + min_val)
            
        h_val_r = ((g - b) / d + (6.0 if g < b else 0.0)) / 6.0
        h_val_g = ((b - r) / d + 2.0) / 6.0
        h_val_b = ((r - g) / d + 4.0) / 6.0
        
        h_val = h_val_r if max_val == r else (h_val_g if max_val == g else h_val_b)
            
        return [h_val * 360.0, s_val * 100.0, l_val * 100.0]

    def _hue_to_rgb(self, p, q, t):
        t_val = t + 1.0 if t < 0.0 else (t - 1.0 if t > 1.0 else t)
        if t_val < 1.0 / 6.0:
            return p + (q - p) * 6.0 * t_val
        if t_val < 1.0 / 2.0:
            return q
        if t_val < 2.0 / 3.0:
            return p + (q - p) * (2.0 / 3.0 - t_val) * 6.0
        return p

    def _hsl_to_hex(self, h, s, l):
        h_norm = h / 360.0
        s_norm = s / 100.0
        l_norm = l / 100.0
        
        r = l_norm
        g = l_norm
        b = l_norm
        
        if s_norm != 0.0:
            q = l_norm * (1.0 + s_norm) if l_norm < 0.5 else l_norm + s_norm - l_norm * s_norm
            p = 2.0 * l_norm - q
            r = self._hue_to_rgb(p, q, h_norm + 1.0 / 3.0)
            g = self._hue_to_rgb(p, q, h_norm)
            b = self._hue_to_rgb(p, q, h_norm - 1.0 / 3.0)
            
        return self._rgb_to_hex(r * 255.0, g * 255.0, b * 255.0)

    def _lighten_color(self, hex_val, percent):
        hsl = self._hex_to_hsl(hex_val)
        h = hsl[0]
        s = hsl[1]
        l = hsl[2]
        new_l = browser.Math.min(100.0, l + percent)
        return self._hsl_to_hex(h, s, new_l)

    def _darken_color(self, hex_val, percent):
        hsl = self._hex_to_hsl(hex_val)
        h = hsl[0]
        s = hsl[1]
        l = hsl[2]
        new_l = browser.Math.max(0.0, l - percent)
        return self._hsl_to_hex(h, s, new_l)

    def _set_alpha(self, hex_val, alpha):
        rgb = self._hex_to_rgb(hex_val)
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        return "rgba(" + str(r) + ", " + str(g) + ", " + str(b) + ", " + str(alpha) + ")"

    def _hex_to_rgb_string(self, hex_val):
        rgb = self._hex_to_rgb(hex_val)
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        return str(r) + ", " + str(g) + ", " + str(b)

    def _get_readable_text_color(self, hex_color):
        try:
            rgb = self._hex_to_rgb(hex_color)
            r = rgb[0] / 255.0
            g = rgb[1] / 255.0
            b = rgb[2] / 255.0
            
            # Map channels to luminance components (matching GhostHub WCAG relative luminance formula)
            r_lum = r / 12.92 if r <= 0.03928 else browser.Math.pow((r + 0.055) / 1.055, 2.4)
            g_lum = g / 12.92 if g <= 0.03928 else browser.Math.pow((g + 0.055) / 1.055, 2.4)
            b_lum = b / 12.92 if b <= 0.03928 else browser.Math.pow((b + 0.055) / 1.055, 2.4)
            
            luminance = 0.2126 * r_lum + 0.7152 * g_lum + 0.0722 * b_lum
            return "#000000" if luminance > 0.5 else "#ffffff"
        except Exception:
            return "#ffffff"

    def _apply_vars(self, primary, accent, background, surface, text):
        root = browser.document.documentElement
        
        accent_rgb = self._hex_to_rgb_string(accent)
        text_rgb = self._hex_to_rgb_string(text)
        soft_accent = "color-mix(in srgb, " + primary + " 78%, " + accent + " 22%)"
        
        # Exact values from GhostHub's themeColors.js
        root.style.setProperty("--primary-color", primary)
        root.style.setProperty("--primary-color-light", self._lighten_color(primary, 15))
        root.style.setProperty("--primary-color-dark", self._darken_color(primary, 15))
        
        root.style.setProperty("--accent-color", accent)
        root.style.setProperty("--accent-color-light", self._lighten_color(accent, 15))
        
        root.style.setProperty("--background-color", background)
        root.style.setProperty("--background-color-dark", self._darken_color(background, 5))
        root.style.setProperty("--background-color-light", self._lighten_color(background, 10))
        
        root.style.setProperty("--surface-color", surface)
        root.style.setProperty("--text-primary", text)
        root.style.setProperty("--text-secondary", self._set_alpha(text, 0.7))
        root.style.setProperty("--text-tertiary", self._set_alpha(text, 0.5))
        
        root.style.setProperty("--card-background", surface)
        root.style.setProperty("--card-hover", "color-mix(in srgb, " + surface + " 88%, " + text + " 12%)")
        root.style.setProperty("--overlay-color", self._set_alpha(background, 0.8))
        
        root.style.setProperty("--primary-color-rgb", self._hex_to_rgb_string(primary))
        root.style.setProperty("--accent-color-rgb", accent_rgb)
        root.style.setProperty("--surface-color-rgb", self._hex_to_rgb_string(surface))
        root.style.setProperty("--background-color-rgb", self._hex_to_rgb_string(background))
        
        root.style.setProperty("--divider-color", self._set_alpha(text, 0.18))
        root.style.setProperty("--divider-color-light", self._set_alpha(text, 0.1))
        
        root.style.setProperty("--gh-surface-solid", self._set_alpha(surface, 0.98))
        root.style.setProperty("--gh-surface-glass", self._set_alpha(surface, 0.9))
        root.style.setProperty("--gh-surface-glass-strong", self._set_alpha(surface, 0.96))
        root.style.setProperty("--gh-surface-pressed", self._set_alpha(text, 0.12))
        
        root.style.setProperty("--gh-border-soft", self._set_alpha(text, 0.12))
        root.style.setProperty("--gh-border-strong", "rgba(" + accent_rgb + ", 0.34)")
        
        root.style.setProperty("--gh-overlay-strong", self._set_alpha(background, 0.82))
        root.style.setProperty("--gh-overlay-immersive", self._set_alpha(background, 0.94))
        root.style.setProperty("--gh-overlay-gradient-bottom", "linear-gradient(transparent, " + self._set_alpha(background, 0.82) + ")")
        
        btn_primary_fg = self._get_readable_text_color(accent)
        root.style.setProperty("--btn-primary-fg", btn_primary_fg)
        
        root.style.setProperty("--btn-secondary-bg", self._set_alpha(surface, 0.96))
        root.style.setProperty("--btn-secondary-bg-hover", "color-mix(in srgb, " + surface + " 88%, " + text + " 12%)")
        root.style.setProperty("--btn-secondary-fg", text)
        root.style.setProperty("--btn-secondary-border", self._set_alpha(text, 0.18))
        
        root.style.setProperty("--btn-ghost-bg-hover", "rgba(" + accent_rgb + ", 0.1)")
        root.style.setProperty("--btn-ghost-fg", self._set_alpha(text, 0.7))
        root.style.setProperty("--btn-ghost-border", self._set_alpha(text, 0.18))
        root.style.setProperty("--btn-icon-bg-hover", "rgba(" + text_rgb + ", 0.08)")
        
        root.style.setProperty("--pill-bg", self._set_alpha(surface, 0.72))
        root.style.setProperty("--pill-border", self._set_alpha(text, 0.18))
        root.style.setProperty("--pill-fg", self._set_alpha(text, 0.7))
        root.style.setProperty("--pill-hover-bg", "rgba(" + accent_rgb + ", 0.14)")
        root.style.setProperty("--pill-hover-fg", text)
        root.style.setProperty("--pill-hover-border", "rgba(" + accent_rgb + ", 0.34)")
        root.style.setProperty("--pill-active-fg", btn_primary_fg)
        
        root.style.setProperty("--input-bg", self._set_alpha(surface, 0.9))
        root.style.setProperty("--input-border", self._set_alpha(text, 0.18))
        root.style.setProperty("--input-fg", text)
        
        root.style.setProperty("--modal-bg", self._set_alpha(surface, 0.96))
        root.style.setProperty("--modal-border", self._set_alpha(text, 0.12))
        
        root.style.setProperty("--card-bg", self._set_alpha(surface, 0.9))
        root.style.setProperty("--card-border", self._set_alpha(text, 0.12))
        
        root.style.setProperty("--theme-soft-accent", soft_accent)
        root.style.setProperty("--theme-soft-accent-muted", "color-mix(in srgb, " + soft_accent + " 16%, transparent)")

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
