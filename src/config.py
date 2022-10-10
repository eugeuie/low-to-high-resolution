from os.path import dirname, abspath, join


base_dir = dirname(dirname(abspath(__file__)))

data_dir = join(base_dir, "data")
models_dir = join(base_dir, "models")
notes_dir = join(base_dir, "notes")

input_data_dir = join(data_dir, "input")

temp_img_path = join(data_dir, "temp.tif")

seed = 42

# MODIS

_modis_bands_filenames = {
    "WINTER1": "priv_mod_v10_2011layer1.img",
    "WINTER2": "priv_mod_v10_2011layer2.img",
    "SPRING1": "2010-05-01.img",
    "SPRING2": "2010-05-02.img",
    "SPRING3": "2010-05-03.img",
    "SUMMER1": "2010-07-01.img",
    "SUMMER2": "2010-07-02.img",
    "SUMMER3": "2010-07-03.img",
    "FALL1": "2010-09-01.img",
    "FALL2": "2010-09-02.img",
    "FALL3": "2010-09-03.img",
}

modis_ru_mask_path = join(input_data_dir, "SubRF_Russia_mask.tif")
modis_sample_path = join(input_data_dir, "lccswm2010_4.img")
modis_classes_legend_path = join(notes_dir, "33class_legend_rus.txt")

modis_sample_classes = [
    "Фон",
    "Темнохвойный лес",
    "Светлохвойный лес",
    "Лиственный лес",
    "Смешанный лес с преобладанием хвойных",
    "Смешанный лес",
    "Смешанный лес с преобладанием лиственных",
    "Хвойный листопадный лес",
    "Редины хвойные листопадные",
    "Луга",
    "Степь",
    "Хвойный кустарник",
    "Лиственный кустарник",
    "Кустарничковая тундра",
    "Травянистая тундра",
    "Кустарниковая тундра",
    "Болота",
    "Прибрежная растительность",
    "Открытые грунты и выходы горных пород",
    "Водные объекты",
]
modis_ru_mask_corrected_path = join(data_dir, "modis_ru_mask.tif")
modis_sample_corrected_path = join(data_dir, "modis_sample.tif")

# Sentinel

_sentinel_filename = "SENTINEL-2B_MSI_20210511_084252"
_sentinel_10m_bands_filenames = {
    "Blue": "SENTINEL-2B_MSI_20210511_084252_channel2_1.tif",
    "Green": "SENTINEL-2B_MSI_20210511_084252_channel3_1.tif",
    "Red": "SENTINEL-2B_MSI_20210511_084252_channel4_1.tif",
    "VNIR": "SENTINEL-2B_MSI_20210511_084252_channel8_1.tif",
}

sentinel_path = join(input_data_dir, _sentinel_filename)
sentinel_10m_bands_paths = {
    name: join(sentinel_path, value)
    for name, value in _sentinel_10m_bands_filenames.items()
}

sentinel_table_data_path = join(
    data_dir,
    f"{_sentinel_filename}_{'_'.join(_sentinel_10m_bands_filenames.keys())}.csv",
)
