import os
from typing import Callable


def filtered_listdir(filter_function: Callable[[str], bool], dir_path: str) -> list:
    names = os.listdir(dir_path)
    paths = list(map(lambda name: os.path.join(dir_path, name), names))
    return sorted(list(filter(filter_function, paths)))


def modis_band_name_from_col_name(col_name: str) -> str:
    bands = {
        1: "Red",
        2: "NIR",
        3: "SWIR",
    }
    band_index = int(col_name[-1])
    return bands[band_index]


