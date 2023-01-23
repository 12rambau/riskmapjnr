import tempfile
import zipfile
from urllib.request import urlretrieve

import ee
import rasterio as rio
from osgeo import gdal
from sepal_ui.scripts import decorator as sd
from tqdm import tqdm


@sd.need_ee
def fcc_from_gfc(calib_start, calib_end, valid_start, valid_end):

    dataset = ee.Image("UMD/hansen/global_forest_change_2021_v1_9")
    thres = 10

    bands = {
        "A": dataset.select("treecover2000"),
        "B": dataset.select("lossyear").unmask(0),
    }

    calc = "fcc = "
    calc += f"(A>{thres})*(B>{calib_start-2000})*(B<={calib_end-2000})*1 + "
    calc += f"(A>{thres})*(B>{valid_start-2000})*(B<={valid_end-2000})*2 + "
    calc += f"(A>{thres})*(B==0)*3"

    filtered_data = (
        dataset.expression(calc, bands).mask(dataset.select("datamask")).int8()
    )

    return filtered_data


@sd.need_ee
def download_fcc(grid, image, dst_dir, alert=None):

    # start the progress bar
    total = len(grid)
    if alert is None:
        pbar = tqdm(total=len(grid), unit="image", unit_scale=True)
    else:
        tqdm_args = {"total": total, "unit": "image", "unit_scale": True}
        alert.update_progress(0, "download images", **tqdm_args)

    # loop in the grid to download each tile
    for i, r in grid.iterrows():
        ee_geometry = ee.Geometry(r.geometry.__geo_interface__)
        link = image.int8().getDownloadURL(
            {
                "name": f"fcc_{i}",
                "region": ee_geometry,
                "filePerBand": False,
                "scale": 30,
                "crs": "EPSG:3857",
            }
        )

        with tempfile.NamedTemporaryFile() as f:
            dst = dst_dir / f"fcc_{i}.tiff"

            if not dst.is_file():
                urlretrieve(link, f.name)
                with zipfile.ZipFile(f.name, "r") as zip_:
                    data = zip_.read(zip_.namelist()[0])
                    dst.write_bytes(data)

                # set nodata to 0
                with rio.open(dst, "r+") as f:
                    f.nodata = 0

        if alert is None:
            pbar.update()
        else:
            alert.update_progress(i + 1, total=total)

    # create a fcc vrt file
    fcc_file = dst_dir / "fcc.vrt"
    filepaths = [str(f) for f in dst_dir.glob("*.tiff")]
    ds = gdal.BuildVRT(str(fcc_file), filepaths)
    ds.FlushCache()

    return fcc_file
