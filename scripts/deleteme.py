"""This script extract all data used during one year of activity.

The input folder (specified as DIRECTORY) has to be organized in the following way:
"""

from pyconsolida.aggregations import load_loop_and_concat
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

file = "/Users/vigji/Desktop/icop/exports/exported-luigi_all-months-_240125-072604/240125-072604_tabellone.pickle"

df = pd.read_pickle(file)
df["data"] = df["data"].apply(lambda x: x + "-01")
# print(df[["anno", "mese", "giorno"]].head())
# Create a datetime column from the year, month, day columns
df["data_dt"] = pd.to_datetime(df["data"], infer_datetime_format=True)

print(df.tail())
