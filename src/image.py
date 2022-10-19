import numpy as np
import pandas as pd
from typing import Tuple, Union
from osgeo import gdal, osr


class Coordinates:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(x={self.x}, y={self.y})"

    def as_list(self) -> list:
        return [self.x, self.y]


class Point(Coordinates):
    ...


class Box:
    def __init__(self, min: Coordinates, max: Coordinates) -> None:
        self.min = min
        self.max = max

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(min={self.min}, max={self.max})"

    @property
    def origin(self) -> Coordinates:
        return Coordinates(x=self.min.x, y=self.max.y)

    def as_list(self) -> list:
        return [self.min.x, self.min.y, self.max.x, self.max.y]


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
    min_x, max_y = geotransform[0], geotransform[3]
    max_x = min_x + x_size * pixel_width
    min_y = max_y + y_size * pixel_height
    box = Box(min=Coordinates(x=min_x, y=min_y), max=Coordinates(x=max_x, y=max_y))
    return box


def get_x_y_sizes_by_box(img_path: str, box: Box) -> Tuple[int, int]:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    img_width = abs(box.min.x - box.max.x)
    img_height = abs(box.min.y - box.max.y)
    x_size = int(np.ceil(abs(img_width / pixel_width)))
    y_size = int(np.ceil(abs(img_height / pixel_height)))
    return x_size, y_size


def get_coordinates_by_point(img_path: str, point: Point) -> Coordinates:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    origin = Coordinates(x=geotransform[0], y=geotransform[3])
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    coordinates = Coordinates(
        x=origin.x + point.x * pixel_width,
        y=origin.y + point.y * pixel_height,
    )
    return coordinates


def get_point_by_coordinates(img_path: str, coordinates: Coordinates) -> Point:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    geotransform = img.GetGeoTransform()
    origin = Coordinates(x=geotransform[0], y=geotransform[3])
    pixel_width, pixel_height = geotransform[1], geotransform[5]
    point = Point(
        x=int((coordinates.x - origin.x) / pixel_width),
        y=int((coordinates.y - origin.y) / pixel_height),
    )
    return point


def get_offset_coordinates(img_path: str, coordinates: Coordinates) -> Coordinates:
    point = get_point_by_coordinates(img_path, coordinates)
    offset_coordinates = get_coordinates_by_point(img_path, point)
    return offset_coordinates


def get_nonzero_data_box(img_path: str) -> Box:
    data = read_data(img_path, flat_data=False)
    nonzero_data_indices = np.argwhere(data != 0)
    xs = nonzero_data_indices[:, 1]
    ys = nonzero_data_indices[:, 0]
    min_point = Point(min(xs), max(ys) + 1)
    max_point = Point(max(xs) + 1, min(ys))
    min_coordinates = get_coordinates_by_point(img_path, min_point)
    max_coordinates = get_coordinates_by_point(img_path, max_point)
    box = Box(min_coordinates, max_coordinates)
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


def crop_by_box(cropped_img_path: str, img_path: str, box: Box) -> None:
    offset_box = Box(
        get_offset_coordinates(img_path, box.min),
        get_offset_coordinates(img_path, box.max),
    )
    gdal.Warp(cropped_img_path, img_path, outputBounds=offset_box.as_list())


def crop_by_nonzero_data_box(cropped_img_path: str, img_path: str) -> None:
    nonzero_data_box = get_nonzero_data_box(img_path)
    crop_by_box(cropped_img_path, img_path, nonzero_data_box)


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
    origin: Union[Coordinates, Point] = Point(0, 0),
    x_size: int = 0,
    y_size: int = 0,
    flat_data: bool = True,
) -> np.ndarray:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    if isinstance(origin, Point):
        origin_point = origin
    else:
        origin_point = get_point_by_coordinates(img_path, origin)
    if x_size == 0:
        x_size, y_size = img.RasterXSize, img.RasterYSize
    band = img.GetRasterBand(1)
    data = band.ReadAsArray(origin_point.x, origin_point.y, x_size, y_size)
    if flat_data:
        data = data.ravel()
    return data


def read_box_data(img_path: str, box: Box, flat_data: bool = True) -> np.ndarray:
    x_size, y_size = get_x_y_sizes_by_box(img_path, box)
    data = read_data(img_path, box.origin, x_size, y_size, flat_data)
    return data


def create(
    img_path: str,
    sample_img_path: str,
    data: np.ndarray,
    origin: Union[Coordinates, Point] = Point(0, 0),
    x_size: int = 0,
    y_size: int = 0,
    flat_data: bool = True,
) -> None:
    sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)

    if isinstance(origin, Point):
        driver = sample_img.GetDriver()
        x_size, y_size = sample_img.RasterXSize, sample_img.RasterYSize
        geotransform = sample_img.GetGeoTransform()

    else:
        fileformat = "GTiff"
        driver = gdal.GetDriverByName(fileformat)
        offset_origin = get_offset_coordinates(sample_img_path, origin)
        geotransform = list(sample_img.GetGeoTransform())
        geotransform[0] = offset_origin.x
        geotransform[3] = offset_origin.y

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
    create(img_path, sample_img_path, data, box.origin, x_size, y_size, flat_data)


def bands_to_csv(
    bands_paths: dict,
    csv_path: str,
    origin: Point = Point(0, 0),
    x_size: int = 0,
    y_size: int = 0,
) -> None:
    data = pd.DataFrame(columns=list(bands_paths.keys()))
    for band in bands_paths:
        data[band] = read_data(bands_paths[band], origin, x_size, y_size)
    data.to_csv(csv_path, index=False)
