"""
The map displayed in the map application.
"""

# from ipyleaflet import WidgetControl

from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw


class MapTile(sw.Tile):
    def __init__(self):
        """
        Specific Map integrating all the widget components.

        Use this map to gather all your widget and place them on it. It will reduce the amount of work to perform in the notebook
        """
        # create a map
        self.m = sm.SepalMap(zoom=3)  # to be visible on 4k screens
        self.m.add_control(
            sm.FullScreenControl(
                self.m, fullscreen=True, fullapp=True, position="topright"
            )
        )

        # create the tile
        super().__init__("map_tile", "", [self.m])

        return
