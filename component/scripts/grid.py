from itertools import product

import geopandas as gpd
import numpy as np
from shapely import geometry as sg


def set_grid(gdf: gpd.GeoDataFrame, size: int = 1):
    """
    compute a grid around a given aoi (ee.FeatureCollection) that is fit for fcc extraction
    The grid cells are tailored to be adapted to always run without timeout

    Args:
        gdf: geodatframe of the aoi geometry
        size: the square size in degrees

    Return:
        the grid in 4326
    """

    # unproject the gdf to 4326
    unproj_gdf = gdf.to_crs(4326)

    # retreive the bounding box
    aoi_bb = sg.box(*unproj_gdf.total_bounds)
    min_x, min_y, max_x, max_y = aoi_bb.bounds

    # create numpy corrdinates table
    lon = np.concatenate([np.arange(min_x, max_x, size), [max_x]])
    lat = np.concatenate([np.arange(min_y, max_y, size), [max_y]])

    # create the grid
    squares = []
    for ix, iy in product(range(len(lon) - 1), range(len(lat) - 1)):

        # fill the grid values
        square = sg.box(lon[ix], lat[iy], lon[ix + 1], lat[iy + 1])
        squares.append(square)

    # create a buffer grid in lat-long
    grid = gpd.GeoDataFrame({"geometry": squares}, crs=4326)

    # final filtering to remove the elements that are out of the initial AOI
    geometry = unproj_gdf.dissolve().geometry.iloc[0]
    grid = grid[grid.intersects(geometry)]

    return grid
