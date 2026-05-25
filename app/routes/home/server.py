from sprag import Controller

from app.theme_data import DEFAULT_PAGE_SIZE, build_theme_catalog


class HomeController(Controller):
    route = "/"

    def load(self):
        index, themes = build_theme_catalog()
        minimal_index = {
            "version": index.get("version", 1),
            "page_size": index.get("page_size", DEFAULT_PAGE_SIZE),
            "total": index.get("total", 0),
            "pages": index.get("pages") or [],
            "records": [],
        }
        return {
            "theme_index": minimal_index,
            "initial_pages": {
                "0": themes[:DEFAULT_PAGE_SIZE],
            },
        }
