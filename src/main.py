import config, utils, image


if __name__ == "__main__":
    # reprojection, 4 min
    projection = image.get_projection(
        img_path=config.SENTINEL_SELECTED_10M_BANDS_PATHS["Red"]
    )
    image.reproject(
        img_path=config.MODIS_SAMPLE_PATH,
        reprojected_img_path=config.MODIS_SAMPLE_REPROJECTED_PATH,
        projection=projection,
    )

    # bands to csv, 5 min
    image.bands_to_csv(
        bands_paths=config.SENTINEL_SELECTED_10M_BANDS_PATHS,
        csv_path=config.SENTINEL_SELECTED_TABLE_DATA_PATH,
    )

    # ...
    ...
