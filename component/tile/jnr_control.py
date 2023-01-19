import multiprocessing as mp

import numpy as np
import rasterio as rio
from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import decorator as sd
from sepal_ui.scripts import utils as su

import riskmapjnr as rmj
from component.message import cm


class TextField(sw.TextField):
    def __init__(self, **kwargs):

        kwargs.setdefault("readonly", True)
        kwargs.setdefault("v_model", None)
        kwargs.setdefault("placeholder", cm.jnr.results.not_computed)

        super().__init__(**kwargs)


class JnrView(sw.Tile):
    def __init__(self, fcc_model):

        # save the models
        self.fcc_model = fcc_model

        # create widgets to display results
        self.w_dist_thresh = TextField(label=cm.jnr.results.dist)
        self.w_window = TextField(label=cm.jnr.results.window)
        self.w_slice = TextField(label=cm.jnr.results.slice)
        self.w_file = TextField(label=cm.jnr.results.file)

        inputs = [self.w_dist_thresh, self.w_window, self.w_slice, self.w_file]

        super().__init__(
            id_="nested",
            title=cm.jnr.title,
            inputs=inputs,
            btn=sw.Btn(cm.jnr.btn),
            alert=sw.Alert(),
        )

        self.btn.on_event("click", self.compute_risk_map)

    @sd.loading_button(debug=True)
    def compute_risk_map(self, *args):

        # check inputs
        su.check_input(self.fcc_model.source)
        su.check_input(self.fcc_model.calib_start)
        su.check_input(self.fcc_model.calib_end)
        su.check_input(self.fcc_model.valid_start)
        su.check_input(self.fcc_model.valid_end)
        su.check_input(self.fcc_model.aoi_name)

        # raise error if the file does not exist
        fcc_vrt = self.fcc_model.fcc_dir() / "fcc.vrt"
        rio.open(fcc_vrt)

        # run riskmapjnr
        ncpu = mp.cpu_count() - 2

        self.alert.add_msg("running process")

        results_makemap = rmj.makemap(
            fcc_file=str(fcc_vrt),
            time_interval=(self.fcc_model.calib_len(), self.fcc_model.valid_len()),
            output_dir=str(self.fcc_model.computation_dir()),
            clean=False,
            dist_bins=np.arange(0, 1080, step=30),
            win_sizes=np.arange(5, 100, 8),
            ncat=30,
            parallel=False,
            ncpu=ncpu,
            methods=["Equal Interval", "Equal Area"],
            csize=40,
            no_quantity_error=True,
            figsize=(6.4, 4.8),
            dpi=100,
            blk_rows=128,
            verbose=False,
        )

        # add the results in the textfields
        ws_hat = results_makemap["ws_hat"]
        m_hat = results_makemap["m_hat"]
        dist_thresh = results_makemap["dist_thresh"]
        fname = f"riskmap_ws{ws_hat}_{m_hat}_ev.tif"
        file = self.fcc_model.computation_dir() / "endval" / fname

        self.w_dist_thresh.v_model = dist_thresh
        self.w_window.v_model = ws_hat
        self.w_slice.v_model = m_hat
        self.w_file.v_model = str(file)

        self.alert.add_msg(cm.jnr.computation_end, "success")


class JnrControl(sm.MenuControl):
    def __init__(self, fcc_model):

        super().__init__(
            icon_content="fa-solid fa-cogs",
            card_content=JnrView(fcc_model),
            card_title=cm.jnr.title,
        )
