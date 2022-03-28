from datetime import datetime
from pathlib import Path

import flammkuchen as fl
import numpy as np
import pandas as pd
from tqdm import tqdm

from pyconsolida.budget_reader import read_full_budget
from pyconsolida.budget_reader_utils import (
    add_tipologia_column,
    fix_types,
    select_costi,
    translate_df,
)
from pyconsolida.df_utils import sum_selected_columns
from pyconsolida.postdoc_fix_utils import (
    check_consistency_of_matches,
    fix_tipologie_df,
    isinlist,
)


def find_all_files(path):
    PATTERNS = ["*nalis*", "*RO-RO*", "*ACC.QUADRO*", "*SPE_GENE*", "*SPE_BRANCH*"]
    possible_files = []
    for pattern in PATTERNS:
        possible_files.extend(list(path.glob(pattern)))

    return possible_files


def read_all_valid_budgets(path, sum_fasi=True):
    files = find_all_files(path)

    loaded = []
    for file in files:
        loaded.append(read_full_budget(file, sum_fasi=sum_fasi))

    loaded = pd.concat(loaded, axis=0, ignore_index=True)

    loaded["commessa"] = path.name
    return loaded


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

# Fogli 2021:
months2021 = sorted(list(master_path.glob("2021/*")))

cantiere_end = dict()
for month in months2021:
    for l in list(month.glob("[0-9][0-9][0-9][0-9]")):
        if l.name not in to_exclude and len(find_all_files(l)) > 0:
            cantiere_end[l.name] = l
folders2021 = [val for _, val in cantiere_end.items()]
all_budgets2021 = []

for folder in folders2021:
    budget = read_all_valid_budgets(folder, sum_fasi=False)
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
for folder in folders2020:
    print(folder)
    budget = read_all_valid_budgets(folder, sum_fasi=False)
    # Somma quantita' e importo complessivo, lo facciamo qui perchè mettiamo assieme
    # piu files:
    budget = sum_selected_columns(budget, "codice", ["quantita", "imp.comp."])
    all_budgets2020.append(budget)

# Load all budgets 2020:
all_budgets2020 = pd.concat(all_budgets2020, axis=0, ignore_index=True)
all_budgets2020 = all_budgets2020[key_sequence]

fix_tipologie_df(
    all_budgets2020,
    tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_2020.xlsx"),
)
all_budgets2020.to_excel(str(dest_dir / f"{tstamp}_tabellone_2020.xlsx"))


# fix_tipologie_df(
#    all_budgets,
#    tipologie_fix,
#    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_2021.xlsx"),
# )
all_budgets2021.to_excel(str(dest_dir / f"{tstamp}_tabellone_2021.xlsx"))

fl.save(
    dest_dir / f"{tstamp}_variable_backup.h5",
    dict(all_budgets2021=all_budgets2021, all_budgets2020=all_budgets2020),
)
