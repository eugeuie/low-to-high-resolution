import numpy as np
import pandas as pd
from typing import Tuple
from osgeo import gdal, osr


def get_projection(img_path: str) -> str:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    projection = img.GetProjection()
    srs = osr.SpatialReference(wkt=projection)
    return f"{srs.GetAttrValue('AUTHORITY', 0)}:{srs.GetAttrValue('AUTHORITY', 1)}"


def reproject(img_path: str, reprojected_img_path: str, projection: str) -> None:
    gdal.Warp(reprojected_img_path, img_path, dstSRS=projection)


def get_relative_x_y(
    img_path: str, absolute_x: int, absolute_y: int
) -> Tuple[int, int]:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    top_left_x, top_left_y = geotransform[0], geotransform[3]
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    relative_x = int((absolute_x - top_left_x) / pixel_width)
    relative_y = int((absolute_y - top_left_y) / pixel_height)
    return relative_x, relative_y


def get_absolute_x_y(img_path: str, relative_x: int, relative_y: int) -> Tuple[int, int]:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    top_left_x, top_left_y = geotransform[0], geotransform[3]
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    absolute_x = top_left_x + relative_x * pixel_width
    absolute_y = top_left_y + relative_y * pixel_height
    return absolute_x, absolute_y


def read_image(
    img_path: str,
    top_left_x: int = 0,
    top_left_y: int = 0,
    x_size: int = None,
    y_size: int = None,
) -> np.array:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    if x_size is None:
        x_size, y_size = img.RasterXSize, img.RasterYSize
    band = img.GetRasterBand(1)
    data = band.ReadAsArray(top_left_x, top_left_y, x_size, y_size)
    data = data.ravel()
    return data


def bands_to_csv(
    bands_paths: dict,
    csv_path: str,
    top_left_x: int = 0,
    top_left_y: int = 0,
    x_size: int = None,
    y_size: int = None,
) -> None:
    data = pd.DataFrame(columns=bands_paths.keys())
    for band in bands_paths:
        data[band] = read_image(bands_paths[band], top_left_x, top_left_y, x_size, y_size)
    data.to_csv(csv_path, index=False)


def create_image(img_path: str, sample_img_path: str, data: np.array, top_left_x: int, top_left_y: int, x_size: int, y_size: int) -> None:
    fileformat = "GTiff"
    driver = gdal.GetDriverByName(fileformat)
    img = driver.Create(img_path, x_size, y_size, bands=1, eType=gdal.GDT_UInt16)

    sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)
    geotransform = list(sample_img.GetGeoTransform())
    geotransform[0] = top_left_x
    geotransform[3] = top_left_y
    img.SetGeoTransform(geotransform)
    projection = sample_img.GetProjection()
    srs = osr.SpatialReference(wkt=projection)
    img.SetProjection(srs.ExportToWkt())

    raster = np.zeros((y_size, x_size), dtype=np.uint8)
    for y in range(y_size):
        for x in range(x_size):
            raster[y][x] = data[x_size * y + x]

    img.GetRasterBand(1).WriteArray(raster)
    img = None


# def create_image(sample_img_path: str, img_path: str, data: np.array) -> None:
#     sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)
#     driver = sample_img.GetDriver()
#     x_size, y_size = sample_img.RasterXSize, sample_img.RasterYSize
#     img = driver.Create(img_path, x_size, y_size, 1, gdal.GDT_UInt16)
#     img.SetGeoTransform(sample_img.GetGeoTransform())
#     img.SetProjection(sample_img.GetProjection())
#     img.GetRasterBand(1).Fill(0)
#     band = img.GetRasterBand(1)
#     raster = np.zeros((y_size, x_size), dtype=np.uint8)
#     for y in range(y_size):
#         for x in range(x_size):
#             raster[y][x] = data[x_size * y + x]
#     band.WriteArray(raster)
#     img = band = None
