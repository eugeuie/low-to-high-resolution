from os.path import dirname, abspath, join


base_dir = dirname(dirname(abspath(__file__)))

data_dir = join(base_dir, "data")
metadata_dir = join(base_dir, "metadata")
models_dir = join(base_dir, "models")

input_data_dir = join(data_dir, "input")

temp_img_path = join(data_dir, "temp.tif")

seed = 42

# MODIS

_modis_dirname = "MODIS-2020"
_modis_input_path = join(input_data_dir, _modis_dirname)

modis_sample_input_path = join(_modis_input_path, "lccswm2020_11.img")
modis_map_input_path = join(_modis_input_path, "2020_map_33class.img")
modis_classes_legend_input_path = join(metadata_dir, "33class_legend_rus.txt")

modis_sample_path = join(data_dir, "modis_sample.tif")
modis_sample_selected_path = join(data_dir, "modis_sample_selected.tif")

# Sentinel

_sentinel_dirname = "SENTINEL-2B_MSI_20210511_084252"
_sentinel_10m_bands_filenames = {
    "Blue": "SENTINEL-2B_MSI_20210511_084252_channel2_1.tif",
    "Green": "SENTINEL-2B_MSI_20210511_084252_channel3_1.tif",
    "Red": "SENTINEL-2B_MSI_20210511_084252_channel4_1.tif",
    "VNIR": "SENTINEL-2B_MSI_20210511_084252_channel8_1.tif",
}

sentinel_input_path = join(input_data_dir, _sentinel_dirname)
sentinel_10m_bands_input_paths = {
    name: join(sentinel_input_path, value)
    for name, value in _sentinel_10m_bands_filenames.items()
}

sentinel_table_data_path = join(
    data_dir,
    f"{_sentinel_dirname}_{'_'.join(_sentinel_10m_bands_filenames.keys())}.csv",
)
