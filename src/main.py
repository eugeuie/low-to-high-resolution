import numpy as np
import time, os
from . import config, utils, image, clustering


def reproject_modis_sample() -> None:
    image.reproject(
        reprojected_img_path=config.modis_sample_path,
        img_path=config.modis_sample_input_path,
        sample_img_path=config.sentinel_10m_bands_input_paths["VNIR"],
    )


def crop_modis_sample() -> None:
    image.crop_by_nonzero_data_box(config.temp_img_path, config.modis_sample_path)
    utils.rename_temp_file(config.temp_img_path, config.modis_sample_path)


def correct_modis_sample_labels() -> None:
    data = image.read_data(config.modis_sample_path)
    ids_classes = utils.parse_classes_legend(config.modis_classes_legend_input_path)
    sample_class_ids = np.unique(data)
    sample_ids_classes = {
        class_id: ids_classes[class_id] for class_id in sample_class_ids
    }

    sample_classes_ids = {}
    sample_classes_unique_ordered = list(dict.fromkeys(sample_ids_classes.values()))
    for name in sample_classes_unique_ordered:
        for class_id, class_name in sample_ids_classes.items():
            if class_name == name:
                sample_classes_ids[name] = sample_classes_ids.get(name, []) + [class_id]

    for ids in sample_classes_ids.values():
        if len(ids) > 1:
            for i in ids[1:]:
                data[data == i] = ids[0]

    image.create(
        img_path=config.temp_img_path,
        sample_img_path=config.modis_sample_path,
        data=data,
    )

    utils.rename_temp_file(config.temp_img_path, config.modis_sample_path)


def set_colors_modis_sample() -> None:
    image.set_color_table(config.modis_sample_path, config.modis_map_input_path)
    image.remove_background(
        config.temp_img_path,
        config.modis_sample_path,
    )
    utils.rename_temp_file(config.temp_img_path, config.modis_sample_path)


def select_territory_from_modis_data() -> None:
    # box = image.get_box(config.sentinel_10m_bands_input_paths["VNIR"])
    def f(file_path: str) -> bool:
        basename = os.path.basename(file_path)
        name, ext = os.path.splitext(basename)
        return name.startswith("KMeans") and ext == ".tif"

    kmeans_labels_imgs_paths = utils.filtered_listdir(f, config.data_dir)
    kmeans_3_clusters_labels_img_path = list(filter(lambda x: "3_" in x, kmeans_labels_imgs_paths))[0]

    box = image.get_box(kmeans_3_clusters_labels_img_path)
    image.crop_by_box(
        config.modis_sample_selected_path, config.modis_sample_path, box
    )


def sentinel_10m_bands_to_csv() -> None:
    image.bands_to_csv(
        bands_paths=config.sentinel_10m_bands_input_paths,
        csv_path=config.sentinel_table_data_path,
    )


def sentinel_10m_bands_chunk_to_csv() -> None:
    image.bands_to_csv(
        bands_paths=config.sentinel_10m_bands_input_paths,
        csv_path=config.sentinel_selected_table_data_path,
        x_size=config.sentinel_selected_data_size,
        y_size=config.sentinel_selected_data_size,
    )


def run_kmeans() -> None:
    for n_clusters in config.kmeans_n_clusters:
        params = {
            "n_clusters": n_clusters,
            "random_state": config.seed
        }
        start = time.time()
        clustering.run_kmeans(
            data_path=config.sentinel_selected_table_data_path,
            params=params,
        )
        print(f"{n_clusters} clusters in {time.time() - start:.2f} sec")


def get_unique_classes_from_modis_selected_data() -> np.ndarray:
    data = image.read_data(config.modis_sample_selected_path)
    return np.unique(data)


if __name__ == "__main__":
    ...
    # reproject_modis_sample()  # 30 sec
    # crop_modis_sample()  # 30 sec
    # correct_modis_sample_labels()  # 4 min
    # set_colors_modis_sample()  # 30 sec
    # sentinel_10m_bands_to_csv()  # 3 min

    # sentinel_10m_bands_selected_to_csv()  # 1 sec

    # run_kmeans()  # 12 min
    # # 3 clusters in 12.11 sec
    # # 5 clusters in 16.76 sec
    # # 10 clusters in 31.95 sec
    # # 20 clusters in 64.78 sec
    # # 30 clusters in 97.77 sec
    # # 40 clusters in 126.24 sec
    # # 100 clusters in 352.04 sec

    # select_territory_from_modis_data()  # 1 sec
    # classes = get_unique_classes_from_modis_selected_data()  # 1 sec