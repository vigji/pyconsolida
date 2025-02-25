# %%
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Create a large mixed-type DataFrame
np.random.seed(42)
num_rows = 10000

df_path = Path("/Users/vigji/Desktop/Analisi_cache_e9d24df73f_93690c.pickle")
df = pd.read_pickle(df_path)

# Define file names
files = {
    "parquet": "data.parquet",
    "pickle": "data.pkl",
    "feather": "data.feather",
    "hdf5": "data.h5",
}


# Benchmarking function
def benchmark_write_read(df, file_format, write_func, read_func):
    # Measure write time
    start = time.time()
    write_func(df, files[file_format])
    write_time = time.time() - start

    # Measure read time
    start = time.time()
    df_loaded = read_func(files[file_format])
    read_time = time.time() - start

    # Measure file size
    file_size = os.path.getsize(files[file_format]) / 1024  # Convert to KB

    return write_time, read_time, file_size


# Store results
results = {}

# Test Parquet
results["Parquet"] = benchmark_write_read(
    df,
    "parquet",
    lambda df, f: df.to_parquet(f, engine="pyarrow", compression="snappy"),
    lambda f: pd.read_parquet(f, engine="pyarrow"),
)

# Test Pickle
results["Pickle"] = benchmark_write_read(
    df, "pickle", lambda df, f: df.to_pickle(f), lambda f: pd.read_pickle(f)
)

# Test Feather
results["Feather"] = benchmark_write_read(
    df, "feather", lambda df, f: df.to_feather(f), lambda f: pd.read_feather(f)
)

# Test HDF5
results["HDF5"] = benchmark_write_read(
    df,
    "hdf5",
    lambda df, f: df.to_hdf(f, key="df", mode="w"),
    lambda f: pd.read_hdf(f, key="df"),
)

# Convert results to DataFrame
benchmark_df = pd.DataFrame(
    results, index=["Write Time (s)", "Read Time (s)", "File Size (KB)"]
).T

benchmark_df
# %%

from pyconsolida.budget_reader import (
    get_folder_hash,
    get_repo_version,
    read_full_budget,
)

file_to_read = Path("/Users/vigji/Desktop/2024/01_Gennaio/1434/Analisi.xlsx")
df, _ = read_full_budget(file_to_read, sum_fasi=False, tipologie_skip=None, cache=False)
# %%
# time reading function. Time 10 times and take the average
start = time.time()
# for _ in range(30):
read_full_budget(file_to_read, sum_fasi=False, tipologie_skip=None, cache=True)
# pd.read_pickle(next(file_to_read.parent.glob("cached/*.pickle")))

# get_repo_version()
# get_folder_hash(file_to_read.parent)
end = time.time()
print(f"Time taken: {(end - start)*1000 } ms")
# %%
