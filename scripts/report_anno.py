from datetime import datetime
from pathlib import Path

from tqdm import tqdm
import pandas as pd

from pyconsolida.posthoc_fix_utils import fix_tipologie_df
from pyconsolida.budget_reader import read_full_budget, sum_selected_columns


def find_all_files(path):
    PATTERNS = ["*nalis*", "*RO-RO*", "*ACC.QUADRO*", "*SPE_GENE*", "*SPE_BRANCH*"]
    possible_files = []
    for pattern in PATTERNS:
        possible_files.extend(list(path.glob(pattern)))

    return possible_files


def read_all_valid_budgets(path, sum_fasi=True):
    files = find_all_files(path)

    loaded = []
    reports = []
    for file in files:
        fasi, cons_report = read_full_budget(file, sum_fasi=sum_fasi)
        loaded.append(fasi)
        if len(cons_report) > 0:
            reports.append(pd.DataFrame(cons_report))

    loaded = pd.concat(loaded, axis=0, ignore_index=True)

    if len(reports) > 0:
        reports = pd.concat(reports, axis=0, ignore_index=True)
        reports["commessa"] = path.name
    else:
        reports = None

    loaded["commessa"] = path.name
    return loaded, reports


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

master_path = Path("/Users/luigipetrucco/Desktop/icop")

to_exclude = ["4004", "9981", "1360", "1445"]

DIRECTORY = master_path

dest_dir = DIRECTORY / "exported_luigi"
dest_dir.mkdir(exist_ok=True)
tipologie_fix = pd.read_excel(DIRECTORY / "tipologie_fix.xlsx")

# timestamp
tstamp = datetime.now().strftime("%y%m%d_%H%M%S")

# All reports
reports = []

# Fogli 2021:
months2021 = sorted(list(master_path.glob("2021/*")))

cantiere_end = dict()
for month in months2021:
    for commessa_folder in list(month.glob("[0-9][0-9][0-9][0-9]")):
        if (
            commessa_folder.name not in to_exclude
            and len(find_all_files(commessa_folder)) > 0
        ):
            cantiere_end[commessa_folder.name] = commessa_folder
folders2021 = [val for _, val in cantiere_end.items()]
all_budgets2021 = []

for folder in tqdm(folders2021):
    budget, rep = read_all_valid_budgets(folder, sum_fasi=True)
    if rep is not None:
        rep["anno"] = "2021"
        reports.append(rep)
    # Somma quantita' e importo complessivo, lo facciamo qui perchè mettiamo assieme
    # piu files:
    budget = sum_selected_columns(budget, "codice", ["quantita", "imp.comp."])
    all_budgets2021.append(budget)
all_budgets2021 = pd.concat(all_budgets2021, axis=0, ignore_index=True)
all_budgets2021 = all_budgets2021[key_sequence]


# Fogli 2020:
folders2020 = list(
    [
        f
        for f in master_path.glob("2020/*/[0-9][0-9][0-9][0-9]")
        if f.name not in to_exclude
    ]
)

all_budgets2020 = []
for folder in tqdm(folders2020):
    budget, rep = read_all_valid_budgets(folder, sum_fasi=True)
    if rep is not None:
        rep["anno"] = "2020"
        reports.append(rep)
    # Somma quantita' e importo complessivo, lo facciamo qui perchè mettiamo assieme
    # piu files:
    budget = sum_selected_columns(budget, "codice", ["quantita", "imp.comp."])
    all_budgets2020.append(budget)

# Load all budgets 2020:
all_budgets2020 = pd.concat(all_budgets2020, axis=0, ignore_index=True)
all_budgets2020 = all_budgets2020[key_sequence]

reports = pd.concat(reports, axis=0, ignore_index=True)
# print(reports)
# fl.save(dest_dir / "reports.h5", reports)

fix_tipologie_df(
    all_budgets2020,
    tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_2020.xlsx"),
)
all_budgets2020.to_excel(str(dest_dir / f"{tstamp}_tabellone_2020.xlsx"))


reports.to_excel(str(dest_dir / f"{tstamp}_voci_costo_fix_report.xlsx"))

# TODO inconsistenze da aggiustare
# fix_tipologie_df(
#    all_budgets,
#    tipologie_fix,
#    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_2021.xlsx"),
# )
all_budgets2021.to_excel(str(dest_dir / f"{tstamp}_tabellone_2021.xlsx"))

# fl.save(
#    dest_dir / f"{tstamp}_variable_backup.h5",
#    dict(all_budgets2021=all_budgets2021, all_budgets2020=all_budgets2020),
# )
