# %%
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

# dest_dir = DIRECTORY / "exports" / f"exported-luigi_all-months-_{tstamp}"
# dest_dir.mkdir(exist_ok=True, parents=True)

if PROGRESS_BAR:
    wrapper = tqdm
else:
    wrapper = lambda x: x

# logging.basicConfig(
#     filename=dest_dir / f"log_{tstamp}.txt",
#     filemode="a",
#     format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
#     datefmt="%H:%M:%S",
#     level=logging.INFO,
# )

# logging.info("Runno estrazione completa...")

# # logger = logging.getLogger("deltaDec")
# # sequence of keys in the final table:
# key_sequence = [
#     "commessa",
#     "fase",
#     "anno",
#     "mese",
#     "data",
#     "codice",
#     "tipologia",
#     "voce",
#     "costo u.",
#     "u.m.",
#     "quantita",
#     "imp. unit.",
#     "imp.comp.",
# ]

# # IDs of works to exclude:
# to_exclude = ["4004", "9981", "1360", "1445"]
# logging.info(f"Escludo commesse specificate: {to_exclude}")

# tipologie_fix = pd.read_excel(DIRECTORY / "tipologie_fix.xlsx")
# logging.info(f"File di correzione tipologie: {DIRECTORY / 'tipologie_fix.xlsx'}")

# tipologie_skip = pd.read_excel(DIRECTORY / "tipologie_skip.xlsx")
# logging.info(f"File di tipologie da saltare: {DIRECTORY / 'tipologie_fix.xlsx'}")

# PATTERNS = [
#         "*nalis*",
#         "*RO-RO*",
#         "*ACC.QUADRO*",
#         "*SPE_GENE*",
#         "*SPE_BRANCH*",
#         "*NALIS*",
#     ]
# SUFFIXES = [".xls", ".xlsx"]
# logging.info(f"Patterns files analisi: {PATTERNS}")
# logging.info(f"Formati files analisi: {SUFFIXES}")


# def find_all_files(path):
#     """Find suitable files for data extraction."""
#     possible_files = []
#     for pattern in PATTERNS:
#         for suffix in SUFFIXES:
#             possible_files.extend(list(path.glob(pattern + suffix)))
#     return possible_files


# def read_all_valid_budgets(path, tipologie_skip=None):
#     """Read valid budget files from a folder.

#     Parameters
#     ----------
#     path : Path obj

#     Returns
#     -------
#         (pd.DataFrame, pd.Dataframe): the loaded data and report on the extractions.
#     """

#     files = find_all_files(path)
#     commessa = path.name
#     mese_raw = path.parent.name[:-1]
#     mese = int(mese_raw.replace(" ", "_").split("_")[-2])
#     anno = int(path.parent.parent.name)
#     data = f"{anno}-{mese:02d}"

#     loaded = []
#     reports = []
#     for file in files:
#         fasi, cons_report = read_full_budget(
#             file, sum_fasi=False, tipologie_skip=tipologie_skip
#         )

#         loaded.append(fasi)
#         if len(cons_report) > 0:
#             reports.append(pd.DataFrame(cons_report))

#     try:
#         loaded = pd.concat(loaded, axis=0, ignore_index=True)
#     except ValueError:
#         # raise RuntimeError(f"No valid files found in {path}")
#         logging.info(f"No file validi in {path}")
#         return None, None

#     loaded["commessa"] = commessa
#     loaded["mese"] = mese
#     loaded["anno"] = anno
#     loaded["data"] = data

#     if len(reports) > 0:
#         reports = pd.concat(reports, axis=0, ignore_index=True)
#         reports["commessa"] = commessa
#         fasi["mese"] = mese
#         fasi["anno"] = anno
#         fasi["data"] = data
#     else:
#         reports = None

#     return loaded, reports


# def _load_loop_and_concat(
#     folders, key_sequence, fix_typology=None, report_filename=None
# ):
#     budgets = []
#     reports = []
#     for folder in wrapper(folders):
#         logging.info(f"Loading {folder}")
#         # try:
#         budget, rep = read_all_valid_budgets(folder, tipologie_skip=tipologie_skip)
#         # except ValueError as e:
#         #     if "Nessuna voce costo valida in file" in str(e):
#         #         logging.info(f"Nessuna voce costo valida per: {folder}; salto")
#         #         continue
#         #     continue
#         if rep is not None:
#             reports.append(rep)
#         budgets.append(budget)

#     budgets = pd.concat(budgets, axis=0, ignore_index=True)
#     budgets = budgets[key_sequence]

#     logging.info(f"File consolidato: {len(budgets)} entrate")

#     if len(reports) > 0:
#         reports = pd.concat(reports, axis=0, ignore_index=True)
#         logging.info(f"Report sul file consolidato: {len(reports)} entrate")

#     if fix_typology is not None:
#         fix_tipologie_df(
#             budgets,
#             tipologie_fix,
#             report_filename=report_filename,
#         )
#         logging.info(f"Correggo le tipologie...")

#     return budgets, reports

all_folders = list(DIRECTORY.glob("202[1-9]/[0-1][0-9]_*/[0-9][0-9][0-9][0-9]"))
# 2021 e 2022 formattazione diversa:
all_folders += list(DIRECTORY.glob("202[1-9]/*_[0-1][0-9]*/[0-9][0-9][0-9][0-9]"))

# Contiamo sull'ordinamento di anni e mesi
all_folders = sorted(all_folders)
print(len(all_folders))

# %%
# Log this:
from pyconsolida.folder_read_utils import months_between_dates, data_from_commessa_folder, get_folder_hash
# sorted(list(set([folder.parent for folder in all_folders])))
# sorted([_data_from_folder(folder) for folder in list(set([folder.parent for folder in all_folders]))])

# %%
all_hashes = pd.DataFrame({get_folder_hash(f) for f in wrapper(all_folders)})
all_hashes
# %%
# %%
# %%
# %%
# for every folder, count months from the first time it was seen:
all_commesse = list(set([folder.name for folder in all_folders]))
commessa = all_commesse[1]
enumerated = [(i, folder) for i, folder in enumerate(all_folders) if folder.name == commessa]


def _data_from_folder(folder):
    # Read year and month from folder and generate a datetime object:
    anno = int(folder.parent.parent.name)
    mese_raw = folder.parent.name.replace(" ", "_").split("_")[-1].lower()
    mese_map = dict(zip(
        ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
         "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
        range(1, 13)
    ))
    mese = mese_map[mese_raw]

    return datetime(anno, mese, 1)

def _months_between_dates(date1, date2):
    "Date difference in number of months"
    date_diff = relativedelta(date1, date2)
    return date_diff.months + date_diff.years * 12

def _months_from_start(folder_list):
    # For every folder, count months from the first time it was seen:
    all_months = [_data_from_folder(folder) for folder in folder_list]
    all_months = sorted(all_months)
    print(all_months)
    return [_months_between_dates(month, all_months[0]) for month in all_months]


_months_from_start([(folder) for folder in (all_folders) if folder.name == commessa])



# logging.info(f"Cartelle da analizzare trovate: {len(all_folders)}")

# budget, reports = _load_loop_and_concat(
#     all_folders,
#     key_sequence,
#     fix_typology=tipologie_fix,
#     report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie.xlsx"),
# )

# budget.to_excel(str(dest_dir / f"{tstamp}_tabellone.xlsx"))

# if len(reports) > 0:
#     reports.to_excel(str(dest_dir / f"{tstamp}_voci-costo_fix_report.xlsx"))

# tipologie_fix.to_excel(str(dest_dir / f"{tstamp}_tipologie-fix.xlsx"))

# %%
import hashlib

def get_file_hash(filename):
    """Compute SHA-256 hash of the specified file."""
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()[:10]

# Example usage
# file_hash = get_file_hash("path/to/your/file")
# print(file_hash)
folder = [(folder) for folder in (all_folders) if folder.name == commessa][0]

# %%
