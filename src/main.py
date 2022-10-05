import config, utils, image


def reproject():
    projection = image.get_projection(
        img_path=config.SENTINEL_SELECTED_10M_BANDS_PATHS["Red"]
    )
    image.reproject(
        img_path=config.MODIS_SAMPLE_PATH,
        reprojected_img_path=config.MODIS_SAMPLE_REPROJECTED_PATH,
        projection=projection,
    )


def bands_to_csv():
    image.bands_to_csv(
        bands_paths=config.SENTINEL_SELECTED_10M_BANDS_PATHS,
        csv_path=config.SENTINEL_SELECTED_TABLE_DATA_PATH,
    )


def select_territory_from_modis_data():
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


if __name__ == "__main__":
    reproject()  # 4 min
    bands_to_csv()  # 5 min
    select_territory_from_modis_data()  # <1 sec
