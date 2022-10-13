import numpy as np
import pandas as pd
from typing import Tuple
from osgeo import gdal, osr


class Point:
    def __init__(self, x: int, y: int, is_abs: bool = True) -> None:
        self.x = x
        self.y = y
        self.is_abs = is_abs


class Box:
    def __init__(self, top_left_point: Point, bottom_right_point: Point) -> None:
        self.top_left_point = top_left_point
        self.bottom_right_point = bottom_right_point

    @property
    def is_abs(self):
        return self.top_left_point.is_abs and self.bottom_right_point.is_abs


def get_projection_code(img_path: str) -> str:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    projection = img.GetProjection()
    srs = osr.SpatialReference(wkt=projection)
    epsg_code = f"{srs.GetAttrValue('AUTHORITY', 0)}:{srs.GetAttrValue('AUTHORITY', 1)}"
    return epsg_code


def get_box(img_path: str) -> Box:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    x_size, y_size = img.RasterXSize, img.RasterYSize
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    top_left_point = Point(x=geotransform[0], y=geotransform[3])
    bottom_right_point = Point(
        x=top_left_point.x + x_size * pixel_width,
        y=top_left_point.y + y_size * pixel_height,
    )
    box = Box(top_left_point, bottom_right_point)
    return box


def get_x_y_sizes_by_box(img_path: str, box: Box) -> Tuple[int, int]:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    img_width = abs(box.top_left_point.x - box.bottom_right_point.x)
    img_height = abs(box.top_left_point.y - box.bottom_right_point.y)
    x_size = int(np.ceil(abs(img_width / pixel_width)))
    y_size = int(np.ceil(abs(img_height / pixel_height)))
    return x_size, y_size


def get_relative_point(img_path: str, point: Point) -> Point:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    top_left_point = Point(x=geotransform[0], y=geotransform[3])
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    relative_point = Point(
        x=int((point.x - top_left_point.x) / pixel_width),
        y=int((point.y - top_left_point.y) / pixel_height),
        is_abs=False,
    )
    return relative_point


def get_offset_point_by_relative_point(img_path: str, relative_point: Point) -> Point:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    top_left_point = Point(x=geotransform[0], y=geotransform[3])
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    offset_point = Point(
        x=top_left_point.x + relative_point.x * pixel_width,
        y=top_left_point.y + relative_point.y * pixel_height,
    )
    return offset_point


def get_offset_point(img_path: str, point: Point) -> Point:
    relative_point = get_relative_point(img_path, point)
    offset_point = get_offset_point_by_relative_point(img_path, relative_point)
    return offset_point


def get_mask_box(mask_path: str) -> Box:
    data = read_data(mask_path, flat_data=False)
    mask_indices = np.argwhere(data == 1)
    xs = mask_indices[:, 1]
    ys = mask_indices[:, 0]
    rel_top_left_point = Point(x=min(xs), y=min(ys), is_abs=False)
    rel_bottom_right_point = Point(x=max(xs) + 1, y=max(ys) + 1, is_abs=False)
    top_left_point = get_offset_point_by_relative_point(mask_path, rel_top_left_point)
    bottom_right_point = get_offset_point_by_relative_point(
        mask_path, rel_bottom_right_point
    )
    box = Box(top_left_point, bottom_right_point)
    return box


def set_color_table(img_path: str, sample_img_path: str) -> None:
    sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)
    sample_band = sample_img.GetRasterBand(1)
    color_table = sample_band.GetRasterColorTable()
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    band = img.GetRasterBand(1)
    band.SetRasterColorTable(color_table)


def reproject(
    reprojected_img_path: str,
    img_path: str,
    sample_img_path: str = "",
    projection_code: str = "",
) -> None:
    if sample_img_path:
        projection_code = get_projection_code(sample_img_path)
    gdal.Warp(reprojected_img_path, img_path, dstSRS=projection_code)


def remove_background(
    no_background_img_path: str, img_path: str, background_value: int = 0
) -> None:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    x_size, y_size = img.RasterXSize, img.RasterYSize
    warp_options = gdal.WarpOptions(
        srcNodata=background_value,
        dstNodata=background_value,
        width=x_size,
        height=y_size,
    )
    gdal.Warp(no_background_img_path, img_path, options=warp_options)


def read_data(
    img_path: str,
    top_left_point: Point = Point(x=0, y=0, is_abs=False),
    x_size: int = 0,
    y_size: int = 0,
    flat_data: bool = True,
) -> np.ndarray:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    if top_left_point.is_abs:
        rel_top_left_point = get_relative_point(img_path, top_left_point)
    else:
        rel_top_left_point = top_left_point
    if x_size == 0:
        x_size, y_size = img.RasterXSize, img.RasterYSize
    band = img.GetRasterBand(1)
    data = band.ReadAsArray(rel_top_left_point.x, rel_top_left_point.y, x_size, y_size)
    if flat_data:
        data = data.ravel()
    return data


def read_box_data(img_path: str, box: Box, flat_data: bool = True) -> np.ndarray:
    x_size, y_size = get_x_y_sizes_by_box(img_path, box)
    data = read_data(img_path, box.top_left_point, x_size, y_size, flat_data)
    return data


def create(
    img_path: str,
    sample_img_path: str,
    data: np.ndarray,
    top_left_point: Point = Point(x=0, y=0, is_abs=False),
    x_size: int = 0,
    y_size: int = 0,
    flat_data: bool = True,
) -> None:
    sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)

    if top_left_point.is_abs:
        fileformat = "GTiff"
        driver = gdal.GetDriverByName(fileformat)
        offset_top_left_point = get_offset_point(sample_img_path, top_left_point)
        geotransform = list(sample_img.GetGeoTransform())
        geotransform[0] = offset_top_left_point.x
        geotransform[3] = offset_top_left_point.y

    else:
        driver = sample_img.GetDriver()
        x_size, y_size = sample_img.RasterXSize, sample_img.RasterYSize
        geotransform = sample_img.GetGeoTransform()

    img = driver.Create(img_path, x_size, y_size, bands=1, eType=gdal.GDT_UInt16)
    img.SetGeoTransform(geotransform)
    img.SetProjection(sample_img.GetProjection())
    img.GetRasterBand(1).Fill(0)

    raster = np.zeros((y_size, x_size), dtype=np.uint8)
    if flat_data:
        for y in range(y_size):
            for x in range(x_size):
                raster[y][x] = data[x_size * y + x]
    else:
        raster = data

    img.GetRasterBand(1).WriteArray(raster)
    img = None


def create_by_box(
    img_path: str,
    sample_img_path: str,
    data: np.ndarray,
    box: Box,
    flat_data: bool = True,
) -> None:
    x_size, y_size = get_x_y_sizes_by_box(sample_img_path, box)
    create(
        img_path, sample_img_path, data, box.top_left_point, x_size, y_size, flat_data
    )


def bands_to_csv(
    bands_paths: dict,
    csv_path: str,
    top_left_point: Point = Point(x=0, y=0, is_abs=False),
    x_size: int = 0,
    y_size: int = 0,
) -> None:
    data = pd.DataFrame(columns=list(bands_paths.keys()))
    for band in bands_paths:
        data[band] = read_data(bands_paths[band], top_left_point, x_size, y_size)
    data.to_csv(csv_path, index=False)
