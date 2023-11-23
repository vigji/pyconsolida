"""This script extract all data used during one year of activity.

The input folder (specified as DIRECTORY) has to be organized in the following way:
"""


import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from pyconsolida.budget_reader import read_full_budget
from pyconsolida.posthoc_fix_utils import fix_tipologie_df

DIRECTORY = Path("/Users/vigji/Desktop/icop")
# YEAR = 2023
PROGRESS_BAR = True

# timestamp for the filename:
tstamp = datetime.now().strftime("%y%m%d-%H%M%S")

dest_dir = DIRECTORY / "exports" / f"exported-luigi_all-months-_{tstamp}"
dest_dir.mkdir(exist_ok=True, parents=True)

if PROGRESS_BAR:
    wrapper = tqdm
else:
    wrapper = lambda x: x

logging.basicConfig(
    filename=dest_dir / f"log_{tstamp}.txt",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)

logging.info("Running complete extraction")

logger = logging.getLogger("deltaDec")
# sequence of keys in the final table:
key_sequence = [
    "commessa",
    "codice",
    "tipologia",
    "voce",
    "costo u.",
    "u.m.",
    "quantita",
    "imp. unit.",
    "imp.comp.",
    "anno",
    "mese",
    "data",
]

# if not SUM_FASI:
key_sequence.insert(1, "fase")

# IDs of works to exclude:
to_exclude = ["4004", "9981", "1360", "1445"]

tipologie_fix = pd.read_excel(DIRECTORY / "tipologie_fix.xlsx")

tipologie_skip = pd.read_excel(DIRECTORY / "tipologie_skip.xlsx")


def find_all_files(path):
    """Find suitable files for data extraction."""
    PATTERNS = [
        "*nalis*",
        "*RO-RO*",
        "*ACC.QUADRO*",
        "*SPE_GENE*",
        "*SPE_BRANCH*",
        "*NALIS*",
    ]
    SUFFIXES = [".xls", ".xlsx"]
    possible_files = []
    for pattern in PATTERNS:
        for suffix in SUFFIXES:
            possible_files.extend(list(path.glob(pattern + suffix)))
    return possible_files


def read_all_valid_budgets(path, tipologie_skip=None):
    """Read valid budget files from a folder.

    Parameters
    ----------
    path : Path obj

    Returns
    -------
        (pd.DataFrame, pd.Dataframe): the loaded data and report on the extractions.
    """

    files = find_all_files(path)
    commessa = path.name
    mese_raw = path.parent.name[:-1]
    mese = int(mese_raw.replace(" ", "_").split("_")[-2])
    anno = int(path.parent.parent.name)
    data = f"{anno}-{mese:02d}"

    loaded = []
    reports = []
    for file in files:
        fasi, cons_report = read_full_budget(
            file, sum_fasi=False, tipologie_skip=tipologie_skip
        )

        loaded.append(fasi)
        if len(cons_report) > 0:
            reports.append(pd.DataFrame(cons_report))

    try:
        loaded = pd.concat(loaded, axis=0, ignore_index=True)
    except ValueError:
        # raise RuntimeError(f"No valid files found in {path}")
        logging.info(f"No file validi in {path}")
        return None, None

    loaded["commessa"] = commessa
    loaded["mese"] = mese
    loaded["anno"] = anno
    loaded["data"] = data

    if len(reports) > 0:
        reports = pd.concat(reports, axis=0, ignore_index=True)
        reports["commessa"] = commessa
        fasi["mese"] = mese
        fasi["anno"] = anno
        fasi["data"] = data
    else:
        reports = None

    return loaded, reports


def _load_loop_and_concat(
    folders, key_sequence, fix_typology=None, report_filename=None
):
    budgets = []
    reports = []
    for folder in wrapper(folders):
        logging.info(f"Loading {folder}")
        # try:
        budget, rep = read_all_valid_budgets(folder, tipologie_skip=tipologie_skip)
        # except ValueError as e:
        #     if "Nessuna voce costo valida in file" in str(e):
        #         logging.info(f"Nessuna voce costo valida per: {folder}; salto")
        #         continue
        #     continue
        if rep is not None:
            # rep["anno"] = f"{YEAR}"
            reports.append(rep)

        # Somma quantita' e importo complessivo, lo facciamo qui perchè mettiamo assieme
        # piu fasi:
        budgets.append(budget)
    budgets = pd.concat(budgets, axis=0, ignore_index=True)

    budgets = budgets[key_sequence]
    if len(reports) > 0:
        reports = pd.concat(reports, axis=0, ignore_index=True)

    if fix_typology is not None:
        fix_tipologie_df(
            budgets,
            tipologie_fix,
            report_filename=report_filename,
        )
    return budgets, reports


all_folders = list(DIRECTORY.glob("202[1-9]/[0-1][0-9]_*/[0-9][0-9][0-9][0-9]"))
all_folders += list(DIRECTORY.glob("202[1-9]/*_[0-1][0-9]_*/[0-9][0-9][0-9][0-9]"))
all_folders = sorted(all_folders)

budget, reports = _load_loop_and_concat(
    all_folders,
    key_sequence,
    fix_typology=tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie.xlsx"),
)

budget.to_excel(str(dest_dir / f"{tstamp}_tabellone.xlsx"))

if len(reports) > 0:
    reports.to_excel(str(dest_dir / f"{tstamp}_voci-costo_fix_report.xlsx"))

tipologie_fix.to_excel(str(dest_dir / f"{tstamp}_tipologie-fix.xlsx"))
