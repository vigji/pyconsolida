"""This script extract all data used during one year of activity.

The input folder (specified as DIRECTORY) has to be organized in the following way:
"""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from pyconsolida.aggregations import load_loop_and_concat
from pyconsolida.delta import get_multiple_date_intervals, get_tabellone_delta

# Change depending on the machine:
DIRECTORY = (
    Path("/Users/vigji/Desktop/Cantieri_test")
    if Path("/Users/vigji").exists()
    else Path("/myshare/cantieri")
)
PROGRESS_BAR = True
OUTPUT_DIR = None  # Path("/Users/vigji/Desktop/exports")
# LOAD_PICKLE = True


# timestamp for the folder name:
tstamp = datetime.now().strftime("%y%m%d-%H%M%S")

# Get all intervals from user
date_intervals = get_multiple_date_intervals()

# Create destination directory using first interval for naming
# first_start, first_stop = date_intervals[0]
if OUTPUT_DIR is None:
    dest_dir = DIRECTORY / "exports" / f"exported_{tstamp}"
else:
    dest_dir = OUTPUT_DIR / f"exported_{tstamp}"

dest_dir.mkdir(exist_ok=True, parents=True)

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename=dest_dir / f"log_{tstamp}.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logging.info("Lancio estrazione...")

# sequence of keys in the final table:
key_sequence = [
    "commessa",
    "fase",
    "anno",
    "mese",
    "data",
    "mesi-da-inizio",
    "codice",
    "tipologia",
    "voce",
    "costo u.",
    "u.m.",
    "quantita",
    "imp. unit.",
    "imp.comp.",
    "file-hash",
]

# IDs of works to exclude:
to_exclude = ["4004", "9981", "1360", "1445"]
logging.info(f"Escludo commesse specificate: {to_exclude}")

tipologie_fix = pd.read_excel(DIRECTORY / "tipologie_fix.xlsx")
logging.info(f"File di correzione tipologie: {DIRECTORY / 'tipologie_fix.xlsx'}")

tipologie_skip = pd.read_excel(DIRECTORY / "tipologie_skip.xlsx")
logging.info(f"File di tipologie da saltare: {DIRECTORY / 'tipologie_fix.xlsx'}")

# Cerca cartelle con ultima versione della formattazione
all_folders = list(DIRECTORY.glob("202[1-9]/[0-1][0-9]_*/*"))

# 2021 e 2022 seguono formattazione diversa:
all_folders += list(DIRECTORY.glob("202[1-9]/*_[0-1][0-9]*/[0-9][0-9][0-9][0-9]*"))
all_folders = sorted([f for f in all_folders if f.is_dir()])
logging.info(f"Cartelle da analizzare trovate: {len(all_folders)}")

# Main loop:
budget, reports = load_loop_and_concat(
    all_folders,
    key_sequence,
    tipologie_fix=tipologie_fix,
    tipologie_skip=tipologie_skip,
    progress_bar=PROGRESS_BAR,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie.xlsx"),
    cache=True,
)

# Uncomment for debugging
budget.to_pickle(str(dest_dir / f"{tstamp}_tabellone.pickle"))
reports.to_pickle(str(dest_dir / f"{tstamp}_reports.pickle"))

# Generate delta for each interval
for start, stop in date_intervals:
    interval_name = f"da{start.date()}-a-{stop.date()}"
    logging.info(f"Calcolo delta per intervallo {interval_name}")

    delta_df = get_tabellone_delta(budget, start, stop)
    delta_df.to_excel(str(dest_dir / f"{tstamp}_delta_tabellone_{interval_name}.xlsx"))

if len(reports) > 0:
    reports.to_excel(str(dest_dir / f"{tstamp}_voci-costo_fix_report.xlsx"))

tipologie_fix.to_excel(str(dest_dir / f"{tstamp}_tipologie-fix.xlsx"))
