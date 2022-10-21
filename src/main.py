import numpy as np
import pandas as pd
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
    kmeans_3_clusters_labels_img_path = list(
        filter(lambda x: "3_" in x, kmeans_labels_imgs_paths)
    )[0]

    box = image.get_box(kmeans_3_clusters_labels_img_path)
    image.crop_by_box(config.modis_sample_selected_path, config.modis_sample_path, box)


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
        params = {"n_clusters": n_clusters, "random_state": config.seed}
        start = time.time()
        clustering.run_kmeans(
            data_path=config.sentinel_selected_table_data_path,
            params=params,
        )
        print(f"{n_clusters} clusters in {time.time() - start:.2f} sec")


def get_kmeans_metrics() -> None:
    kmeans_metrics = pd.DataFrame(
        columns=[
            "n_clusters",
            "inertia",
            "silhouette_coef",
            "calinski_harabasz_index",
            "davies_bouldin_index",
        ]
    )

    def f(file_path: str) -> bool:
        basename = os.path.basename(file_path)
        name, ext = os.path.splitext(basename)
        return name.startswith("KMeans")

    models_paths = utils.filtered_listdir(f, config.models_dir)

    models_paths_sorted = []
    for n in config.kmeans_n_clusters:
        for model_path in models_paths:
            basename = os.path.basename(model_path)
            if f"{n}_" in basename:
                models_paths_sorted.append(model_path)
                break

    for i, n in enumerate(config.kmeans_n_clusters):
        start = time.time()
        metrics = clustering.get_kmeans_metrics(
            config.sentinel_selected_table_data_path, models_paths_sorted[i]
        )
        end = time.time()
        kmeans_metrics.loc[i] = [n] + metrics

        print(f"metrics for {n} clusters calculated in {end - start:.2f} sec")

    kmeans_metrics.to_csv(config.kmeans_metrics_path, index=False)


def get_unique_classes_from_modis_selected_data() -> np.ndarray:
    data = image.read_data(config.modis_sample_selected_path)
    return np.unique(data)


def get_kmeans_5_clusters_stats() -> None:
    modis_x_size, modis_y_size = image.get_x_y_sizes(config.modis_sample_selected_path)
    modis_x_size -= 1
    modis_y_size -= 1

    modis_data = image.read_data(
        config.modis_sample_selected_path,
        origin=image.Point(1, 1),
        x_size=modis_x_size,
        y_size=modis_y_size,
        flat_data=False,
    )

    nonzero_modis_data_indices = np.argwhere(modis_data != 0)
    x_indices = nonzero_modis_data_indices[:, 1] + 1
    y_indices = nonzero_modis_data_indices[:, 0] + 1
    stats = pd.DataFrame({"modis_point_x": x_indices, "modis_point_y": y_indices})
    modis_points = [image.Point(x, y) for x, y in zip(x_indices, y_indices)]
    coordinates = [
        image.get_coordinates_by_point(config.modis_sample_selected_path, point)
        for point in modis_points
    ]
    coordinates = np.array([coordinate.as_list() for coordinate in coordinates])
    x_coordinates = coordinates[:, 0]
    y_coordinates = coordinates[:, 1]

    stats["modis_class"] = modis_data[modis_data != 0]
    stats["coordinate_x"] = x_coordinates
    stats["coordinate_y"] = y_coordinates

    for n in range(config.selected_n_clusters):
        stats[f"sentinel_class_{n}_count"] = 0

    stats["sentinel_majority_class"] = pd.NA

    modis_pixel_x_size, modis_pixel_y_size = image.get_pixel_x_y_sizes(
        config.modis_sample_selected_path
    )
    left, top = x_coordinates[0], y_coordinates[0]
    right = left + modis_pixel_x_size
    bottom = top - modis_pixel_y_size
    box = image.Box(image.Coordinates(left, bottom), image.Coordinates(right, top))

    sentinel_x_size, sentinel_y_size = image.get_x_y_sizes_by_box(
        config.selected_clustered_img_path, box
    )

    for i in range(len(x_coordinates)):
        sentinel_data = image.read_data(
            config.selected_clustered_img_path,
            image.Coordinates(x_coordinates[i], y_coordinates[i]),
            sentinel_x_size,
            sentinel_y_size,
        )

        unique, counts = np.unique(sentinel_data, return_counts=True)

        for j in range(len(unique)):
            stats.at[i, f"sentinel_class_{unique[j]}_count"] = counts[j]

        stats.at[i, "sentinel_majority_class"] = unique[counts.argmax()]

    stats.to_csv(config.selected_n_clusters_stats_path, index=False)


if __name__ == "__main__":
    ...
    # reproject_modis_sample()  # 30 sec
    # crop_modis_sample()  # 30 sec
    # correct_modis_sample_labels()  # 4 min
    # set_colors_modis_sample()  # 30 sec
    # sentinel_10m_bands_to_csv()  # 3 min
    # image.color_table_to_txt(config.modis_sample_path, config.modis_classes_color_table_path)  # 1 secF

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
