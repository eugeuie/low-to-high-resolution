import os
import numpy as np
import config, utils, image


def reproject_modis_data() -> None:
    image.reproject(
        reprojected_img_path=config.modis_ru_mask_path,
        img_path=config.modis_ru_mask_input_path,
        sample_img_path=config.sentinel_10m_bands_input_paths["VNIR"],
    )

    image.reproject(
        reprojected_img_path=config.modis_sample_path,
        img_path=config.modis_sample_input_path,
        sample_img_path=config.sentinel_10m_bands_input_paths["VNIR"],
    )


def crop_modis_data() -> None:
    mask_box = image.get_mask_box(config.modis_ru_mask_path)

    data = image.read_box_data(config.modis_ru_mask_path, mask_box)
    data[data != 1] = 0
    image.create_by_box(config.temp_img_path, config.modis_ru_mask_path, data, mask_box)
    utils.rename_temp_file(config.temp_img_path, config.modis_ru_mask_path)

    data = image.read_box_data(config.modis_sample_path, mask_box)
    image.create_by_box(config.temp_img_path, config.modis_sample_path, data, mask_box)
    utils.rename_temp_file(config.temp_img_path, config.modis_sample_path)


def correct_modis_sample_labels() -> None:
    data = image.read_data(config.modis_sample_path)
    ids_classes = utils.parse_classes_legend(config.modis_classes_legend_input_path)
    sample_class_ids = np.unique(data)
    sample_ids_classes = {
        class_id: ids_classes[class_id] for class_id in sample_class_ids
    }

    sample_classes_ids = {}
    for name in config.modis_sample_classes:
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
    
    image.set_color_table(config.modis_sample_path, config.modis_sample_input_path)
    utils.rename_temp_file(config.temp_img_path, config.modis_sample_path)


def remove_background() -> None:
    image.remove_background(
        config.modis_sample_path,
        config.temp_img_path,
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
    
    # reproject_modis_data()  # 2 min
    # crop_modis_data()  # 9 min
    # correct_modis_sample_labels()  # 5 min
    # remove_background()  # 30 sec
    # select_territory_from_modis_data()  # <1 sec

    # bands_to_csv()  # 5 min
