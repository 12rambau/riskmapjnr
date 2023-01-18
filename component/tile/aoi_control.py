import ee
from sepal_ui import aoi
from sepal_ui import color as sc
from sepal_ui import mapping as sm
from sepal_ui.message import ms
from sepal_ui.scripts import utils as su

from component.message import cm


class AoiView(aoi.AoiView):
    """
    Extend the aoi_view component from sepal_ui.mapping to add
    the extra coloring parameter used in this application. To do so we were
    forced to copy/paste the _update_aoi
    """

    def __init__(self, **kwargs):

        # create the map
        super().__init__(methods=["-POINTS"], **kwargs)

        # nest the tile
        self.elevation = False

        # change btn color
        self.btn.color = "secondary"

    @su.loading_button(debug=False)
    def _update_aoi(self, widget, event, data):
        """
        extention of the original method that display information on the map.
        In the ee display we changed the display parameters
        """
        self.model.geo_json = self.aoi_dc.to_json()

        # update the model
        self.model.set_object()
        self.alert.add_msg(ms.aoi_sel.complete, "success")

        # update the map
        self.map_.remove_layer("aoi", none_ok=True)
        self.map_.zoom_bounds(self.model.total_bounds())

        empty = ee.Image().byte()
        fc = self.model.feature_collection
        outline = empty.paint(featureCollection=fc, color=1, width=2)
        self.map_.addLayer(outline, {"palette": sc.primary}, "aoi")

        self.aoi_dc.hide()

        # tell the rest of the apps that the aoi have been updated
        self.updated += 1

        return self


class AoiControl(sm.MenuControl):
    def __init__(self, m):

        # create the view
        self.view = AoiView(map_=m)
        self.view.class_list.add("ma-5")

        # create the control
        super().__init__(
            "fa-solid fa-map-marker-alt", self.view, m=m, card_title=cm.aoi.title
        )
