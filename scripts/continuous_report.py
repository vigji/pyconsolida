"""This script extract all data used during one year of activity.

The input folder (specified as DIRECTORY) has to be organized in the following way:
"""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from pyconsolida.aggregations import load_loop_and_concat

DIRECTORY = Path("/Users/vigji/Desktop/icop")
PROGRESS_BAR = True

# timestamp for the filename:
tstamp = datetime.now().strftime("%y%m%d-%H%M%S")

dest_dir = DIRECTORY / "exports" / f"exported-luigi_all-months-_{tstamp}"
dest_dir.mkdir(exist_ok=True, parents=True)


logging.basicConfig(
    filename=dest_dir / f"log_{tstamp}.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logging.info("Lancio estrazione completa...")

# logger = logging.getLogger("deltaDec")
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

all_folders = list(DIRECTORY.glob("202[1-9]/[0-1][0-9]_*/1475"))
# 2021 e 2022 formattazione diversa:
all_folders += list(DIRECTORY.glob("202[1-9]/*_[0-1][0-9]*/1475"))
all_folders = sorted(all_folders)
logging.info(f"Cartelle da analizzare trovate: {len(all_folders)}")

budget, reports = load_loop_and_concat(
    all_folders,
    key_sequence,
    tipologie_fix=tipologie_fix,
    tipologie_skip=tipologie_skip,
    progress_bar=PROGRESS_BAR,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie.xlsx"),
)

budget.to_excel(str(dest_dir / f"{tstamp}_tabellone.xlsx"))

if len(reports) > 0:
    reports.to_excel(str(dest_dir / f"{tstamp}_voci-costo_fix_report.xlsx"))

tipologie_fix.to_excel(str(dest_dir / f"{tstamp}_tipologie-fix.xlsx"))
