from sprag import Screen, hydrate

from .components import ThemeGalleryShell
from .modules import ThemeGalleryModule


class HomeScreen(Screen):
    modules = [ThemeGalleryModule]

    def render(self, data):
        module = self.module(ThemeGalleryModule)
        module.set_state(data)
        return hydrate(ThemeGalleryShell, module=module)
