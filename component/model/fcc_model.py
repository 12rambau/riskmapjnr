from sepal_ui import model
from traitlets import Int, Unicode

from component import parameter as cp


class FccModel(model.Model):

    # inputs
    source = Unicode(None, allow_none=True).tag(sync=True)
    calib_start = Int(None, allow_none=True).tag(sync=True)
    calib_end = Int(None, allow_none=True).tag(sync=True)
    valid_start = Int(None, allow_none=True).tag(sync=True)
    valid_end = Int(None, allow_none=True).tag(sync=True)
    aoi_name = Unicode(None, allow_none=True).tag(sync=True)

    def computation_dir(self):

        dates = "_".join(
            [
                str(e)
                for e in [
                    self.calib_start,
                    self.calib_end,
                    self.valid_start,
                    self.valid_end,
                ]
            ]
        )

        dir_name = f"{self.aoi_name}_{self.source}_{dates}"

        computation_dir = cp.result_dir / dir_name
        computation_dir.mkdir(exist_ok=True)

        return computation_dir

    def fcc_dir(self):

        fcc_dir = self.computation_dir() / "fcc"
        fcc_dir.mkdir(exist_ok=True)

        return fcc_dir

    def calib_len(self):

        return self.calib_end - self.calib_start

    def valid_len(self):

        return self.valid_end - self.valid_start
