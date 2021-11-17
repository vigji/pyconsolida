from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from pyconsolida.budget_reader import read_full_budget
from pyconsolida.postdoc_fix_utils import (
    check_consistency_of_matches,
    fix_tipologie_df,
    isinlist,
)

DIRECTORY = Path(r"C:\Users\lpetrucco\Desktop\Sostenibilità_biennio19_20")

dest_dir = DIRECTORY / "exported_luigi"
dest_dir.mkdir(exist_ok=True)

# Trova tutti i file analisi:
file_analisi_list = list(DIRECTORY.glob("[0-9]*[0-9]*[0-9]*[0-9]/*nalisi*.xls"))

settori_map = pd.read_excel(DIRECTORY / "settori_map.xlsx").set_index("commessa")
tipologie_map = pd.read_excel(DIRECTORY / "tipologie_map.xlsx").set_index("da")
tipologie_fix = pd.read_excel(DIRECTORY / "tipologie_fix.xlsx")
categorie_map = pd.read_excel(DIRECTORY / "categorie_map.xlsx")

# Commesse file di input:
all_commesse = set([int(f.parent.name) for f in file_analisi_list])

# controlla corrispondenza 1:1 nomi cartelle e id commesse nel file settori_map.xlsx
no_settore_defined = all_commesse - set(settori_map.index)
no_analisi_file = set(settori_map.index) - all_commesse
if len(no_settore_defined) > 0:
    print(f"Nessun settore definito in settori_map.xlsx per: {no_settore_defined}")
if len(no_analisi_file) > 0:
    print(f"Nessun file di analisi per: {no_analisi_file}")

# Riordinamento colonne per il file esportato:
tstamp = datetime.now().strftime("%y%m%d_%H%M%S")

key_sequence = [
    "commessa",
    "settore",
    "codice",
    "tipologia",
    "voce",
    "u.m.",
    "quantita",
    "costo u.",
    "imp.comp.",
]

all_costi = []
for filename in tqdm(file_analisi_list):
    # Nome cantiere da cartella:
    commessa = int(filename.parent.name)

    # Filtra cantieri che hanno un settore definito nel file di mapping
    if commessa not in no_settore_defined:
        all_fasi_concat = read_full_budget(filename, sum_fasi=True)
        all_fasi_concat["commessa"] = commessa

        all_costi.append(all_fasi_concat)

# Concatena tutte le commesse:
concatenated = pd.concat(all_costi, axis=0, ignore_index=True)

# Mappa settori:
concatenated["settore"] = concatenated["commessa"].map(settori_map["settore"])

# Trasforma tipologie dopo aver controllato di aver una mappa per tutte:
assert (
    len([i for i in concatenated["tipologia"].unique() if i not in tipologie_map.index])
    == 0
)
concatenated["tipologia"] = concatenated["tipologia"].map(tipologie_map["a"])

# Riordina tabella:
concatenated = concatenated[key_sequence]

fix_tipologie_df(
    concatenated,
    tipologie_fix,
    report_filename=str(dest_dir / f"{tstamp}_fixed_tipologie.xlsx"),
)

categorie_map = pd.read_excel(DIRECTORY / "categorie_map.xlsx")
matches = isinlist(
    concatenated,
    categorie_map,
    se_contiene_key="e contiene",
    se_tipologia_key="se tipologia",
)
check_consistency_of_matches(
    matches, concatenated["voce"], categorie_map, mapped_label_key="allora"
)

# Once this is safe, we can just use the matches interchangably:
indexes_to_change = np.argwhere(matches)

# Fix inplace tipologia in the dataframe:
prev = indexes_to_change[0, 0]

concatenated["categoria"] = concatenated["tipologia"].copy()
for i, j in indexes_to_change:
    # sanity check - would not work because of duplicated vals, hence the prev:
    if i != prev:
        assert concatenated.loc[i, "tipologia"] == categorie_map.loc[j, "se tipologia"]
    concatenated.loc[i, "categoria"] = categorie_map.loc[j, "allora"]

    prev = i

# Salva con timestamp:
concatenated.to_excel(str(dest_dir / f"{tstamp}_tabellone.xlsx"))
