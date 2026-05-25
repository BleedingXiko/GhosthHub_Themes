from sprag import Controller

from app.theme_data import DEFAULT_PAGE_SIZE, build_theme_catalog


class HomeController(Controller):
    route = "/"

    def load(self):
        index, themes = build_theme_catalog()
        return {
            "theme_index": index,
            "initial_pages": {
                "0": themes[:DEFAULT_PAGE_SIZE],
            },
        }
