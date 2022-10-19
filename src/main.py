import os
import numpy as np
from . import config, utils, image


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


# def bands_to_csv() -> None:
#     image.bands_to_csv(
#         bands_paths=config.SENTINEL_SELECTED_10M_BANDS_PATHS,
#         csv_path=config.SENTINEL_SELECTED_TABLE_DATA_PATH,
#     )


def select_territory_from_modis_data() -> None:
    (
        abs_top_left_x,
        abs_top_left_y,
        abs_bottom_right_x,
        abs_bottom_right_y,
    ) = image.get_box(config.sentinel_10m_bands_input_paths["VNIR"])
    selected_data = image.read_data(
        config.modis_sample_path,
        abs_top_left_x,
        abs_top_left_y,
        abs_bottom_right_x,
        abs_bottom_right_y,
    )
    selected_data_x_size, selected_data_y_size = image.get_x_y_sizes_by_box(
        config.modis_sample_path,
        abs_top_left_x,
        abs_top_left_y,
        abs_bottom_right_x,
        abs_bottom_right_y,
    )
    image.create(
        config.modis_sample_selected_path,
        config.modis_sample_path,
        selected_data,
        abs_top_left_x,
        abs_top_left_y,
        selected_data_x_size,
        selected_data_y_size,
    )
    image.remove_background(
        config.modis_sample_selected_path,
        config.temp_img_path,
    )
    os.remove(config.modis_sample_selected_path)
    os.rename(config.temp_img_path, config.modis_sample_selected_path)
    image.set_color_table(
        config.modis_sample_selected_path, config.modis_sample_input_path
    )


if __name__ == "__main__":
    ...
    # reproject_modis_sample()  # 30 sec
    # crop_modis_sample()  # 30 sec
    # correct_modis_sample_labels()  # 4 min
    # set_colors_modis_sample()  # 30 sec

    # select_territory_from_modis_data()  # <1 sec

    # bands_to_csv()  # 5 min
