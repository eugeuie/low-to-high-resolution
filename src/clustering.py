import numpy as np
import pandas as pd
from os.path import join
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)
from joblib import dump, load
from . import config, image


def run_kmeans(data_path: str, params: dict) -> None:
    data = pd.read_csv(data_path, index_col=False)
    
    kmeans = KMeans()
    kmeans.set_params(**params)
    kmeans.fit(data)

    filename = f"{type(kmeans).__name__}_{kmeans.n_clusters}_clusters"
    model_path = join(config.models_dir, f"{filename}.joblib")
    labels_path = join(config.data_dir, f"{filename}_labels.csv")
    img_path = join(config.data_dir, f"{filename}_labels.tif")
    
    dump(kmeans, model_path)

    kmeans_labels = pd.Series(kmeans.labels_)
    kmeans_labels.to_csv(labels_path, index=False)

    kmeans_labels = np.array(kmeans_labels).ravel()
    image.create(
        img_path=img_path,
        sample_img_path=config.sentinel_10m_bands_input_paths["VNIR"],
        data=kmeans_labels,
        x_size=config.sentinel_selected_data_size,
        y_size=config.sentinel_selected_data_size,
    )
