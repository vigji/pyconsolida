"""This script extract all data used during one year of activity.

The input folder (specified as DIRECTORY) has to be organized in the following way:
"""


from datetime import datetime
from pathlib import Path

import flammkuchen as fl
import pandas as pd
from tqdm import tqdm

from pyconsolida.budget_reader import read_full_budget, sum_selected_columns
from pyconsolida.posthoc_fix_utils import fix_tipologie_df

DIRECTORY = Path("/Users/vigji/Desktop/icop")
YEAR = 2022

dest_dir = DIRECTORY / "exported_luigi"

# sequence of keys in the final table:
key_sequence = [
    "commessa",
    "codice",
    "tipologia",
    "voce",
    "u.m.",
    "quantita",
    "costo u.",
    "imp.comp.",
]

# IDs of works to exclude:
to_exclude = ["4004", "9981", "1360", "1445"]

dest_dir.mkdir(exist_ok=True)
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


def read_all_valid_budgets(path, sum_fasi=True):
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
    except ValueError as e:
        print(e)
        raise RuntimeError(f"No valid files found in {path}")

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
    for folder in tqdm(folders):
        budget, rep = read_all_valid_budgets(folder, sum_fasi=True)
        if rep is not None:
            rep["anno"] = f"{YEAR}"
            reports.append(rep)
        # Somma quantita' e importo complessivo, lo facciamo qui perchè mettiamo assieme
        # piu fasi:
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


# timestamp for the filename:
tstamp = datetime.now().strftime("%y%m%d_%H%M%S")

# All reports
reports = []
months = sorted(list(DIRECTORY.glob(f"{YEAR}/*")))
print(f"Found {len(months)} folders")

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
        for f in DIRECTORY.glob(f"{YEAR-1}/*cembr*/[0-9][0-9][0-9][0-9]")
        if f.name not in to_exclude
    ]
)
budgets_dec, reports_dec = _load_loop_and_concat(
    folders_dec,
    key_sequence,
    fix_typology=tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_{YEAR-1}.xlsx"),
)

# Load most recent budget for every work id
budgets, reports = _load_loop_and_concat(
    folders,
    key_sequence,
    fix_typology=tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_{YEAR}.xlsx"),
)


for budget, report, year in zip(
    [budgets_dec, budgets], [reports_dec, reports], [YEAR - 1, YEAR]
):
    budget.to_excel(str(dest_dir / f"{tstamp}_tabellone_{year}.xlsx"))
    reports.to_excel(str(dest_dir / f"{tstamp}_voci_costo_fix_report_{year}.xlsx"))

tipologie_fix.to_excel(str(dest_dir / f"{tstamp}_tipologie_fix_file.xlsx"))

fl.save(
    dest_dir / f"{tstamp}_python_data.h5",
    dict(budgets_dec=budgets_dec, budgets=budgets),
)
