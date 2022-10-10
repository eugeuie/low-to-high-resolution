import os
import numpy as np
import config as config, utils, image


def reproject_modis_data() -> None:
    """Reprojection of MODIS sample and Russia mask for MODIS sample into Sentinel data projection."""
    image.reproject(
        img_path=config.modis_ru_mask_path,
        reprojected_img_path=config.modis_ru_mask_corrected_path,
        sample_img_path=config.sentinel_10m_bands_paths["VNIR"],
    )
    image.reproject(
        img_path=config.modis_sample_path,
        reprojected_img_path=config.modis_sample_corrected_path,
        sample_img_path=config.sentinel_10m_bands_paths["VNIR"],
    )


def correct_modis_sample_labels() -> None:
    """Correcting classes labels for MODIS sample."""
    data = image.read_data(config.modis_sample_corrected_path)
    ids_classes = utils.parse_classes_legend(config.modis_classes_legend_path)
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

    image.create_image(
        img_path=config.temp_img_path,
        sample_img_path=config.modis_sample_corrected_path,
        data=data,
    )

    os.remove(config.modis_sample_corrected_path)
    os.rename(config.temp_img_path, config.modis_sample_corrected_path)

    image.set_color_table(
        img_path=config.modis_sample_corrected_path,
        sample_img_path=config.modis_sample_path,
    )





# def bands_to_csv() -> None:
#     image.bands_to_csv(
#         bands_paths=config.SENTINEL_SELECTED_10M_BANDS_PATHS,
#         csv_path=config.SENTINEL_SELECTED_TABLE_DATA_PATH,
#     )


# def select_territory_from_modis_data() -> None:
#     (
#         abs_top_left_x,
#         abs_top_left_y,
#         abs_bottom_right_x,
#         abs_bottom_right_y,
#     ) = image.get_image_bbox(config.SENTINEL_SELECTED_10M_BANDS_PATHS["VNIR"])
#     selected_data = image.read_image(
#         config.MODIS_SAMPLE_REPROJECTED_CORRECT_LABELS_PATH,
#         abs_top_left_x,
#         abs_top_left_y,
#         abs_bottom_right_x,
#         abs_bottom_right_y,
#     )
#     selected_data_x_size, selected_data_y_size = image.get_x_y_size_by_bbox(
#         config.MODIS_SAMPLE_REPROJECTED_CORRECT_LABELS_PATH,
#         abs_top_left_x,
#         abs_top_left_y,
#         abs_bottom_right_x,
#         abs_bottom_right_y,
#     )
#     image.create_image(
#         config.MODIS_SELECTED_DATA_PATH,
#         config.MODIS_SAMPLE_REPROJECTED_CORRECT_LABELS_PATH,
#         selected_data,
#         abs_top_left_x,
#         abs_top_left_y,
#         selected_data_x_size,
#         selected_data_y_size,
#     )


# def remove_background() -> None:
# image.remove_background(
#     config.MODIS_SELECTED_DATA_PATH,
#     config.MODIS_SELECTED_NO_BACKGROUND_PATH,
# )


if __name__ == "__main__":
    reproject_modis_data()  # 2 min
    correct_modis_sample_labels()  # 9 min

    # bands_to_csv()  # 5 min
    # select_territory_from_modis_data()  # <1 sec
    # remove_background()  # <1 min
