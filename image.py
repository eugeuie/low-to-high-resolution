import numpy as np
from osgeo import gdal


def read_image(img_path: str) -> np.array:
    img = gdal.Open(img_path, gdal.GA_ReadOnly)
    x_size, y_size = img.RasterXSize, img.RasterYSize
    band = img.GetRasterBand(1)
    band_data = band.ReadAsArray(0, 0, x_size, y_size)
    band_data = band_data.ravel()
    img = band = None
    return band_data


def create_image(sample_img_path: str, img_path: str, data: np.array) -> None:
    sample_img = gdal.Open(sample_img_path, gdal.GA_ReadOnly)
    driver = sample_img.GetDriver()
    x_size, y_size = sample_img.RasterXSize, sample_img.RasterYSize
    img = driver.Create(img_path, x_size, y_size, 1, gdal.GDT_UInt16)
    img.SetGeoTransform(sample_img.GetGeoTransform())
    img.SetProjection(sample_img.GetProjection())
    img.GetRasterBand(1).Fill(0)
    band = img.GetRasterBand(1)
    raster = np.zeros((y_size, x_size), dtype=np.uint8)
    for y in range(y_size):
        for x in range(x_size):
            raster[y][x] = data[x_size * y + x]
    band.WriteArray(raster)
    img = band = None
