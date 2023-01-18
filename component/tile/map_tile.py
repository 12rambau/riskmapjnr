"""
The map displayed in the map application.
"""

from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw

from .about_control import AboutControl
from .aoi_control import AoiControl
from .fcc_control import FccControl


class MapTile(sw.Tile):
    def __init__(self):
        """
        Specific Map integrating all the widget components.

        Use this map to gather all your widget and place them on it. It will reduce the amount of work to perform in the notebook
        """
        # create a map
        self.m = sm.SepalMap(zoom=3)  # to be visible on 4k screens
        vic = sm.ValueInspector(m=self.m)
        fsc = sm.FullScreenControl(self.m, True, True, position="topright")
        self.m.add_control(fsc)
        self.m.add_control(vic)

        # add the workflow controls
        about_control = AboutControl()
        aoi_control = AoiControl(self.m)
        fcc_control = FccControl(aoi_control.view.model, self.m)

        # add them on the map
        self.m.add_control(about_control)
        self.m.add_control(fcc_control)
        self.m.add_control(aoi_control)

        # create the tile
        super().__init__("map_tile", "", [self.m])

        return
