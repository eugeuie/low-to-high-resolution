import numpy as np
import pandas as pd
from typing import Tuple
from osgeo import gdal, osr


def get_projection(img_path: str) -> str:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    projection = img.GetProjection()
    srs = osr.SpatialReference(wkt=projection)
    epsg_code = f"{srs.GetAttrValue('AUTHORITY', 0)}:{srs.GetAttrValue('AUTHORITY', 1)}"
    return epsg_code


def reproject(
    img_path: str,
    reprojected_img_path: str,
    sample_img_path: str = None,
    projection: str = None,
) -> None:
    if sample_img_path:
        projection = get_projection(sample_img_path)
    gdal.Warp(reprojected_img_path, img_path, dstSRS=projection)


def get_bbox(img_path: str) -> Tuple[int, int, int, int]:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    x_size, y_size = img.RasterXSize, img.RasterYSize
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    top_left_x = geotransform[0]
    top_left_y = geotransform[3]
    bottom_right_x = top_left_x + x_size * pixel_width
    bottom_right_y = top_left_y + y_size * pixel_height
    return top_left_x, top_left_y, bottom_right_x, bottom_right_y


def get_x_y_size_by_bbox(
    img_path: str,
    abs_top_left_x: int,
    abs_top_left_y: int,
    abs_bottom_right_x: int,
    abs_bottom_right_y: int,
) -> Tuple[int, int]:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    image_width = abs(abs_top_left_x - abs_bottom_right_x)
    image_height = abs(abs_top_left_y - abs_bottom_right_y)
    x_size = int(abs(image_width / pixel_width))
    y_size = int(abs(image_height / pixel_height))
    return x_size, y_size


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


def get_offset_absolute_x_y(
    img_path: str, relative_x: int, relative_y: int
) -> Tuple[int, int]:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    top_left_x, top_left_y = geotransform[0], geotransform[3]
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    absolute_x = top_left_x + relative_x * pixel_width
    absolute_y = top_left_y + relative_y * pixel_height
    return absolute_x, absolute_y


def read_data(
    img_path: str,
    abs_top_left_x: int = 0,
    abs_top_left_y: int = 0,
    abs_bottom_right_x: int = None,
    abs_bottom_right_y: int = None,
    x_size: int = None,
    y_size: int = None,
) -> np.array:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)

    if abs_top_left_x != 0:
        rel_top_left_x, rel_top_left_y = get_relative_x_y(
            img_path, abs_top_left_x, abs_top_left_y
        )
    else:
        rel_top_left_x, rel_top_left_y = abs_top_left_x, abs_top_left_y

    if x_size is None:
        if abs_bottom_right_x is None:
            x_size, y_size = img.RasterXSize, img.RasterYSize
        else:
            x_size, y_size = get_x_y_size_by_bbox(
                img_path,
                abs_top_left_x,
                abs_top_left_y,
                abs_bottom_right_x,
                abs_bottom_right_y,
            )

    band = img.GetRasterBand(1)
    data = band.ReadAsArray(rel_top_left_x, rel_top_left_y, x_size, y_size)
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
        data[band] = read_data(
            bands_paths[band], top_left_x, top_left_y, x_size, y_size
        )
    data.to_csv(csv_path, index=False)


def create_image(
    img_path: str,
    sample_img_path: str,
    data: np.array,
    abs_top_left_x: int = None,
    abs_top_left_y: int = None,
    x_size: int = None,
    y_size: int = None,
) -> None:
    sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)

    if abs_top_left_x is not None:
        rel_top_left_x, rel_top_left_y = get_relative_x_y(
            sample_img_path, abs_top_left_x, abs_top_left_y
        )
        offset_abs_top_left_x, offset_abs_top_left_y = get_offset_absolute_x_y(
            sample_img_path, rel_top_left_x, rel_top_left_y
        )

        fileformat = "GTiff"
        driver = gdal.GetDriverByName(fileformat)
        img = driver.Create(img_path, x_size, y_size, bands=1, eType=gdal.GDT_UInt16)

        geotransform = list(sample_img.GetGeoTransform())
        geotransform[0] = offset_abs_top_left_x
        geotransform[3] = offset_abs_top_left_y
        img.SetGeoTransform(geotransform)
        projection = sample_img.GetProjection()
        srs = osr.SpatialReference(wkt=projection)
        img.SetProjection(srs.ExportToWkt())

    else:
        driver = sample_img.GetDriver()
        x_size, y_size = sample_img.RasterXSize, sample_img.RasterYSize
        img = driver.Create(img_path, x_size, y_size, 1, gdal.GDT_UInt16)
        img.SetGeoTransform(sample_img.GetGeoTransform())
        img.SetProjection(sample_img.GetProjection())
        img.GetRasterBand(1).Fill(0)

    raster = np.zeros((y_size, x_size), dtype=np.uint8)
    for y in range(y_size):
        for x in range(x_size):
            raster[y][x] = data[x_size * y + x]

    img.GetRasterBand(1).WriteArray(raster)
    img = None


def remove_background(
    img_path: str, no_background_img_path: str, background_value: int = 0
) -> None:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    x_size, y_size = img.RasterXSize, img.RasterYSize
    warp_options = gdal.WarpOptions(
        srcNodata=0, dstNodata=background_value, width=x_size, height=y_size
    )
    gdal.Warp(no_background_img_path, img_path, options=warp_options)


def get_color_table(img_path: str) -> None:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    band = img.GetRasterBand(1)
    color_table = band.GetRasterColorTable()
    return color_table


def set_color_table(img_path: str, sample_img_path: str) -> None:
    sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)
    sample_band = sample_img.GetRasterBand(1)
    color_table = sample_band.GetRasterColorTable()
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    band = img.GetRasterBand(1)
    band.SetRasterColorTable(color_table)
