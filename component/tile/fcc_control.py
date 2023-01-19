from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import decorator as sd
from sepal_ui.scripts import utils as su
from traitlets import directional_link

from component import parameter as cp
from component import scripts as cs
from component.message import cm
from component.model import FccModel


class FccView(sw.Tile):
    def __init__(self, aoi_model, m):

        # gather aoi_model
        self.aoi_model = aoi_model

        # add a map
        self.m = m

        # create the wigdgets
        self.w_source = sw.Select(
            label=cm.fcc.source.label, v_model=None, items=cp.fcc_inputs
        )

        items = [i for i in range(2022, 1999, -1)]
        calib_label = sw.Html(tag="h4", children=cm.fcc.calib.label)
        self.w_calib_start = sw.Select(
            class_="mr-5", label=cm.fcc.calib.start, v_model=None, items=items
        )
        self.w_calib_end = sw.Select(label=cm.fcc.calib.end, v_model=None, items=items)
        calib_line = sw.Flex(
            class_="d-flex", children=[self.w_calib_start, self.w_calib_end]
        )
        w_calib = sw.Col(children=[calib_label, calib_line])

        valid_label = sw.Html(tag="h4", children=cm.fcc.valid.label)
        self.w_valid_start = sw.Select(
            class_="mr-5", label=cm.fcc.valid.start, v_model=None, items=items
        )
        self.w_valid_end = sw.Select(label=cm.fcc.valid.end, v_model=None, items=items)
        valid_line = sw.Flex(
            class_="d-flex", children=[self.w_valid_start, self.w_valid_end]
        )
        w_valid = sw.Col(children=[valid_label, valid_line])

        inputs = [self.w_source, w_calib, w_valid]

        # wire everything to a fcc_model
        self.fcc_model = (
            FccModel()
            .bind(self.w_source, "source")
            .bind(self.w_calib_start, "calib_start")
            .bind(self.w_calib_end, "calib_end")
            .bind(self.w_valid_start, "valid_start")
            .bind(self.w_valid_end, "valid_end")
        )
        directional_link((self.aoi_model, "name"), (self.fcc_model, "aoi_name"))

        super().__init__(
            id_="nested",
            title=cm.fcc.title,
            inputs=inputs,
            btn=sw.Btn(cm.fcc.btn),
            alert=sw.Alert(),
        )

        # add js behavior
        self.btn.on_event("click", self.compute_fcc)

    @sd.loading_button(debug=True)
    def compute_fcc(self, *args):

        # check inputs
        su.check_input(self.fcc_model.source)
        su.check_input(self.fcc_model.calib_start)
        su.check_input(self.fcc_model.calib_end)
        su.check_input(self.fcc_model.valid_start)
        su.check_input(self.fcc_model.valid_end)
        su.check_input(self.aoi_model.name)

        # check that date make sense
        m = self.fcc_model
        if not (m.calib_start < m.calib_end <= m.valid_start < m.valid_end):
            raise Exception(cm.fcc.wrong_order)

        # get the ee image
        fcc_data = cs.fcc_from_gfc(
            self.fcc_model.calib_start,
            self.fcc_model.calib_end,
            self.fcc_model.valid_start,
            self.fcc_model.valid_end,
        )

        # create a grid around the aoi
        grid = cs.set_grid(self.aoi_model.gdf)

        # download the images
        fc = fcc_data.select("fcc").clip(self.aoi_model.feature_collection)
        cs.download_fcc(
            grid=grid,
            image=fc.unmask(),
            dst_dir=self.fcc_model.fcc_dir(),
            alert=self.alert,
        )

        # display on the map
        self.m.addLayer(fc, cp.fcc_display, cm.fcc.layer)
        self.m.zoom_ee_object(fc)

        self.alert.add_msg(cm.fcc.layer_loaded, "success")


class FccControl(sm.MenuControl):
    def __init__(self, aoi_model, m):

        self.view = FccView(aoi_model, m)

        super().__init__(
            icon_content="fa-solid fa-tree",
            card_content=self.view,
            card_title=cm.fcc.title,
        )
