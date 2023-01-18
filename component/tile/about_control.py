from pathlib import Path

from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw

from component.message import cm


class AboutControl(sm.MenuControl):
    def __init__(self):

        about_content = Path(__file__).parents[2] / "utils" / cm.about.pathname

        about_tile = sw.TileAbout(about_content)

        super().__init__(
            icon_content="fa-solid fa-question",
            card_content=about_tile,
            position="bottomleft",
        )
