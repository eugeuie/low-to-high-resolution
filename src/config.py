from os.path import dirname, abspath, join

base_dir = dirname(dirname(abspath(__file__)))

data_dir = join(base_dir, "data")
models_dir = join(base_dir, "models")

raw_data_dir = join(data_dir, "raw")
interim_data_dir = join(data_dir, "interim")
processed_data_dir = join(data_dir, "processed")
