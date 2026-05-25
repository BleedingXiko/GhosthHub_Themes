from sprag import page

from .server import HomeController
from .web import HomeScreen


home = page(
    path="/",
    controller=HomeController,
    screen=HomeScreen,
    mode="hybrid",
    css=["app/routes/home/home.css"],
    metadata={
        "title": "GhostHub Themes — Community Theme Gallery",
        "description": "Browse and import community-built themes for GhostHub.",
    },
)
