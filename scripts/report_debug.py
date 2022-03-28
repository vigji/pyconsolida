from datetime import datetime
from pathlib import Path

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


master_path = Path("/Users/luigipetrucco/Desktop/icop")

to_exclude = ["4004", "9981", "1360"]

# timestamp
tstamp = datetime.now().strftime("%y%m%d_%H%M%S")

folders2020 = list(
    [
        f
        for f in master_path.glob("2020/*/[0-9][0-9][0-9][0-9]")
        if f.name not in to_exclude
    ]
)
all_budgets_2020 = []
folders = [
    Path("/Users/luigipetrucco/Desktop/icop/2021/21_12 Dicembre/1417"),
]
# Path("/Users/luigipetrucco/Desktop/icop/2020/20_12_Dicembre 2020/9991")]
for folder in folders:
    all_budgets_2020.append(read_all_valid_budgets(folder, sum_fasi=True))


# all_budgets_2020 = pd.concat(all_budgets_2020, axis=0, ignore_index=True)


# all_budgets_2020 = all_budgets_2020[key_sequence]

# fix_tipologie_df(
#    all_budgets_2020,
#    tipologie_fix,
#    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_2020.xlsx"),
# )
# all_budgets_2020.to_excel(str(dest_dir / f"{tstamp}_tabellone_2020.xlsx"))

# fix_tipologie_df(
#    all_budgets,
#    tipologie_fix,
#    report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie_2021.xlsx"),
# )
