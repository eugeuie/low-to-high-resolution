import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_DATA_DIR = os.path.join(DATA_DIR, "input")

MODELS_DIR = os.path.join(BASE_DIR, "models")

HIGH_RES_DATA_DIRS = [
    "LANDSAT_8_OLI_TIRS_20210604_082849",
    "LANDSAT_8_OLI_TIRS_20210706_082857",
    "SENTINEL-2A_MSI_20200901_053433",
    "SENTINEL-2A_MSI_20200921_053434",
    "SENTINEL-2A_MSI_20201117_084357",
    "SENTINEL-2A_MSI_20210327_052418",
    "SENTINEL-2A_MSI_20220524_053423",
    "SENTINEL-2B_MSI_20190425_085420",
    "SENTINEL-2B_MSI_20190813_053920",
    "SENTINEL-2B_MSI_20210325_085404",
    "SENTINEL-2B_MSI_20210511_084252",
    "SENTINEL-2B_MSI_20210531_052344",
    "SENTINEL-2B_MSI_20210703_053405",
    "SENTINEL-2B_MSI_20211008_084414",
]

MODIS_MASK_FILENAME = "SubRF_Russia_mask.tif"
MODIS_SAMPLE_FILENAME = "lccswm2010_4.img"
MODIS_BANDS_FILENAMES = {
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

SENTINEL_SELECTED_DATA_DIR = "SENTINEL-2B_MSI_20210511_084252"
SENTINEL_SELECTED_DATA_PATH = os.path.join(INPUT_DATA_DIR, SENTINEL_SELECTED_DATA_DIR)
SENTINEL_SELECTED_10M_BANDS_FILENAMES = {
    "Blue": "SENTINEL-2B_MSI_20210511_084252_channel2_1.tif",
    "Green": "SENTINEL-2B_MSI_20210511_084252_channel3_1.tif",
    "Red": "SENTINEL-2B_MSI_20210511_084252_channel4_1.tif",
    "VNIR": "SENTINEL-2B_MSI_20210511_084252_channel8_1.tif",
}

MODIS_SAMPLE_PATH = os.path.join(INPUT_DATA_DIR, MODIS_SAMPLE_FILENAME)

SENTINEL_SELECTED_10M_BANDS_PATHS = {
    name: os.path.join(SENTINEL_SELECTED_DATA_PATH, value)
    for name, value in SENTINEL_SELECTED_10M_BANDS_FILENAMES.items()
}

_name, _ext = os.path.splitext(MODIS_SAMPLE_FILENAME)
MODIS_SAMPLE_REPROJECTED_FILENAME = f"{_name}_reprojected{_ext}"
MODIS_SAMPLE_REPROJECTED_PATH = os.path.join(
    DATA_DIR, MODIS_SAMPLE_REPROJECTED_FILENAME
)
MODIS_SELECTED_DATA_FILENAME = f"{_name}_selected.tif"
MODIS_SELECTED_DATA_PATH = os.path.join(DATA_DIR, MODIS_SELECTED_DATA_FILENAME)

SENTINEL_SELECTED_TABLE_DATA_FILENAME = f"{SENTINEL_SELECTED_DATA_DIR}_{'_'.join(SENTINEL_SELECTED_10M_BANDS_FILENAMES.keys())}.csv"
SENTINEL_SELECTED_TABLE_DATA_PATH = os.path.join(
    DATA_DIR, SENTINEL_SELECTED_TABLE_DATA_FILENAME
)


TEST_PATH = os.path.join(DATA_DIR, "test.tif")

SEED = 42
