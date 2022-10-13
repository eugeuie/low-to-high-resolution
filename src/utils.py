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


def parse_classes_legend(legend_path: str) -> dict:
    classes = {}
    with open(legend_path, mode="rt", encoding="utf-8") as f:
        for line in f:
            key, value = line.rstrip().split(". ")
            classes[int(key)] = value
    return classes


def rename_temp_file(temp_file_path: str, dst_file_path: str) -> None:
    os.remove(dst_file_path)
    os.rename(temp_file_path, dst_file_path)
