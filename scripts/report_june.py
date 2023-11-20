"""This script extract all data used during one year of activity.

The input folder (specified as DIRECTORY) has to be organized in the following way:
"""


import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from pyconsolida.budget_reader import read_full_budget, sum_selected_columns
from pyconsolida.posthoc_fix_utils import fix_tipologie_df

DIRECTORY = Path("/Users/vigji/Desktop/icop")
YEAR = 2023
SUM_FASI = False
PROGRESS_BAR = False


# timestamp for the filename:
tstamp = datetime.now().strftime("%y%m%d-%H%M%S")
dest_dir = DIRECTORY / f"exported-luigi-deltagiugno_sum-fasi-{SUM_FASI}_{tstamp}"
dest_dir.mkdir(exist_ok=True)

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

logging.info("Running 2022 delta")

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
]
if not SUM_FASI:
    key_sequence.insert(1, "fase")

# IDs of works to exclude:
to_exclude = ["4004", "9981", "1360", "1445"]

tipologie_fix = pd.read_excel(DIRECTORY / "tipologie_fix.xlsx")


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
    possible_files = []
    for pattern in PATTERNS:
        possible_files.extend(list(path.glob(pattern)))

    return possible_files


def read_all_valid_budgets(path, sum_fasi):
    """Read valid budget files from a folder.

    Parameters
    ----------
    path : Path obj
    sum_fasi : bool
        Whether or not to sum across construction phases.

    Returns
    -------
        (pd.DataFrame, pd.Dataframe): the loaded data and report on the extractions.
    """

    files = find_all_files(path)

    loaded = []
    reports = []
    for file in files:
        fasi, cons_report = read_full_budget(file, sum_fasi=sum_fasi)
        loaded.append(fasi)
        if len(cons_report) > 0:
            reports.append(pd.DataFrame(cons_report))

    try:
        loaded = pd.concat(loaded, axis=0, ignore_index=True)
    except ValueError:
        # raise RuntimeError(f"No valid files found in {path}")
        logging.info(f"No files validi in {path}")
        return None, None

    if len(reports) > 0:
        reports = pd.concat(reports, axis=0, ignore_index=True)
        reports["commessa"] = path.name
    else:
        reports = None

    loaded["commessa"] = path.name
    return loaded, reports


def _load_loop_and_concat(
    folders, key_sequence, fix_typology=None, report_filename=None
):
    budgets = []
    reports = []
    for folder in wrapper(folders):
        logging.info(f"Loading {folder}")
        try:
            budget, rep = read_all_valid_budgets(folder, sum_fasi=SUM_FASI)
        except ValueError as e:
            if "Nessuna voce costo valida in file" in str(e):
                logging.info(f"Nessuna voce costo valida per: {folder}; salto")
                continue
            continue
        if rep is not None:
            rep["anno"] = f"{YEAR}"
            reports.append(rep)
        # Somma quantita' e importo complessivo, lo facciamo qui perchè mettiamo assieme
        # piu fasi:
        if SUM_FASI:
            budget = sum_selected_columns(budget, "codice", ["quantita", "imp.comp."])
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


# All reports:
reports = []
months = sorted(list(DIRECTORY.glob(f"{YEAR}/[0-1][0-9]_*")))
print(months)
print("Taking: ")
months = months[:-1]  # exclude last incomplete month
print(months)

# In this loop we find the start and end of each construction site by looking at last
# folder containing valid data for that site:
cantiere_end = dict()  # dict to keep track of all the ends
for month in months:
    # Loop over project ids:
    for commessa_folder in list(month.glob("[0-9][0-9][0-9][0-9]")):
        # Save end as last valid folder:
        if (
            commessa_folder.name not in to_exclude
            and len(find_all_files(commessa_folder)) > 0
        ):
            cantiere_end[commessa_folder.name] = commessa_folder

folders = [val for _, val in cantiere_end.items()]


# Find works that were already started in December last year:
folders_dec = list(
    [
        f
        for f in DIRECTORY.glob(f"{YEAR}/*iugn*/[0-9][0-9][0-9][0-9]")
        if f.name not in to_exclude
    ]
)
budgets_dec, reports_dec = _load_loop_and_concat(
    folders_dec,
    key_sequence,
    fix_typology=tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_giugno.xlsx"),
)

# Load most recent budget for every work id
budgets, reports = _load_loop_and_concat(
    folders,
    key_sequence,
    fix_typology=tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_ottogre.xlsx"),
)


for budget, report, lab in zip(
    [budgets_dec, budgets], [reports_dec, reports], ["giugno", "ottobre"]
):
    budget.to_excel(str(dest_dir / f"{tstamp}_tabellone_{lab}.xlsx"))
    reports.to_excel(str(dest_dir / f"{tstamp}_voci-costo_fix_report-{lab}.xlsx"))

tipologie_fix.to_excel(str(dest_dir / f"{tstamp}_tipologie-fix.xlsx"))


# Sezione per calcolare i delta, non serve piu:
# import flammkuchen as fl
# fl.save(
#     dest_dir / f"{tstamp}_python_data.h5",
#     dict(budgets_dec=budgets_dec, budgets=budgets),
# )

# Compute deltas:
# data_dict = fl.load(dest_dir / f"{tstamp}_python_data.h5")
# numerical = ["quantita", "imp. unit.", "imp.comp."]
# budgets_tot, budgets_dec = data_dict["budgets"], data_dict["budgets_dec"]

# budgets_tot = budgets_tot.set_index(["commessa", "codice", "fase"]).drop(
#     ["costo u."], axis=1
# )
# budgets_dec = budgets_dec.set_index(["commessa", "codice", "fase"]).drop(
#     ["costo u."], axis=1
# )

# dec_al, tot_al = budgets_dec.align(budgets_tot)
# dec_al.loc[:, numerical] = dec_al.loc[:, numerical].fillna(0)
# tot_al.loc[:, numerical] = tot_al.loc[:, numerical].fillna(0)

# for col in ["quantita", "imp.comp."]:
#     deltas = tot_al[col] - dec_al[col]
#     deltas.to_csv(dest_dir / f"{tstamp}_deltas_{col}.csv")
#     deltas[deltas < 0].to_excel(dest_dir / f"{tstamp}_negative-deltas.csv")
