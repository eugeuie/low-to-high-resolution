import numpy as np
import config, utils, image


def reproject() -> None:
    projection = image.get_projection(
        img_path=config.SENTINEL_SELECTED_10M_BANDS_PATHS["Red"]
    )
    image.reproject(
        img_path=config.MODIS_SAMPLE_PATH,
        reprojected_img_path=config.MODIS_SAMPLE_REPROJECTED_PATH,
        projection=projection,
    )


def bands_to_csv() -> None:
    image.bands_to_csv(
        bands_paths=config.SENTINEL_SELECTED_10M_BANDS_PATHS,
        csv_path=config.SENTINEL_SELECTED_TABLE_DATA_PATH,
    )


def select_territory_from_modis_data() -> None:
    (
        abs_top_left_x,
        abs_top_left_y,
        abs_bottom_right_x,
        abs_bottom_right_y,
    ) = image.get_image_bbox(config.SENTINEL_SELECTED_10M_BANDS_PATHS["VNIR"])
    selected_data = image.read_image(
        config.MODIS_SAMPLE_REPROJECTED_PATH,
        abs_top_left_x,
        abs_top_left_y,
        abs_bottom_right_x,
        abs_bottom_right_y,
    )
    selected_data_x_size, selected_data_y_size = image.get_x_y_size_by_bbox(
        config.MODIS_SAMPLE_REPROJECTED_PATH,
        abs_top_left_x,
        abs_top_left_y,
        abs_bottom_right_x,
        abs_bottom_right_y,
    )
    image.create_image(
        config.MODIS_SELECTED_DATA_PATH,
        config.MODIS_SAMPLE_REPROJECTED_PATH,
        selected_data,
        abs_top_left_x,
        abs_top_left_y,
        selected_data_x_size,
        selected_data_y_size,
    )


def get_modis_data_with_correct_labels() -> None:
    data = image.read_image(config.MODIS_SAMPLE_REPROJECTED_PATH)
    classes_legend = utils.parse_modis_classes_names(config.MODIS_CLASSES_LEGEND_PATH)
    classes = np.unique(data)
    classes_legend = {key: classes_legend[key] for key in classes}

    classes_ids = {}
    for name in config.MODIS_CLASSES_NAMES:
        for class_id, class_name in classes_legend.items():
            if class_name == name:
                classes_ids[name] = classes_ids.get(name, []) + [class_id]

    for ids in classes_ids.values():
        if len(ids) > 1:
            for i in ids[1:]:
                data[data == i] = ids[0]

    image.create_image(
        config.MODIS_SAMPLE_REPROJECTED_CORRECT_LABELS_PATH,
        config.MODIS_SAMPLE_REPROJECTED_PATH,
        data,
    )


def remove_background() -> None:
    ...


if __name__ == "__main__":
    reproject()  # 25 sec
    bands_to_csv()  # 5 min
    select_territory_from_modis_data()  # <1 sec
    get_modis_data_with_correct_labels()  # 9 min
