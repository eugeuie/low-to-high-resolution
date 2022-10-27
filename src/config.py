from os.path import dirname, abspath, join

# Directory paths

base_dir = dirname(dirname(abspath(__file__)))

data_dir = join(base_dir, "data")
metadata_dir = join(base_dir, "metadata")
models_dir = join(base_dir, "models")

input_dir = join(data_dir, "input")
processing_dir = join(data_dir, "processing")
stats_dir = join(data_dir, "stats")
temp_dir = join(data_dir, "temp")

# Input data paths (lr for low resolution, hr for high resolution data)

lr_sample_input_path = join(input_dir, "MODIS-2020/lccswm2020_11.img")
lr_map_input_path = join(input_dir, "2020_map_33class.img")
lr_legend_input_path = join(input_dir, "33class_legend_rus.txt")

_hr_data_dirs = ["SENTINEL-2A_MSI_20201117_084357", ]

# High resolution data

_sentinel_dirname = "SENTINEL-2B_MSI_20210511_084252"
_sentinel_10m_bands_filenames = {
    "Blue": "SENTINEL-2B_MSI_20210511_084252_channel2_1.tif",
    "Green": "SENTINEL-2B_MSI_20210511_084252_channel3_1.tif",
    "Red": "SENTINEL-2B_MSI_20210511_084252_channel4_1.tif",
    "VNIR": "SENTINEL-2B_MSI_20210511_084252_channel8_1.tif",
}

sentinel_input_path = join(input_dir, _sentinel_dirname)
sentinel_10m_bands_input_paths = {
    name: join(sentinel_input_path, value)
    for name, value in _sentinel_10m_bands_filenames.items()
}

sentinel_table_data_path = join(
    data_dir,
    f"{_sentinel_dirname}_{'_'.join(_sentinel_10m_bands_filenames.keys())}.csv",
)

sentinel_selected_data_size = 2000
sentinel_selected_table_data_path = join(data_dir, "sentinel_selected.csv")

# Clustering

kmeans_n_clusters = [3, 5, 10, 20, 30, 40, 100]
kmeans_metrics_path = join(metadata_dir, "kmeans_metrics.csv")

selected_n_clusters = 30
selected_clustered_img_path = join(data_dir, f"KMeans_{selected_n_clusters}_clusters_labels.tif")
# selected_clustered_img_path = join(
#     data_dir,
#     "SENTINEL-2B_MSI_20210511_084252_kmeans_20_clusters_labels_trained_on_Blue_Red_Green_VNIR.tif",
# )

selected_n_clusters_stats_path = join(
    stats_dir, f"kmeans_{selected_n_clusters}_clusters_stats.csv"
)
