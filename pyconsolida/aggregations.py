import logging

import pandas as pd
from tqdm import tqdm

from pyconsolida.budget_reader import read_full_budget_cached
from pyconsolida.budget_reader_utils import get_folder_hash
from pyconsolida.folder_read_utils import (
    data_from_commessa_folder,
    months_between_dates,
)
from pyconsolida.posthoc_fix_utils import fix_tipologie_df
from pyconsolida.sheet_specs import KEY_SEQUENCE, PATTERNS, SUFFIXES

logging.info(f"Patterns files analisi: {PATTERNS}")
logging.info(f"Formati files analisi: {SUFFIXES}")


def find_all_files(path):
    """Find suitable files for data extraction."""
    possible_files = []
    for pattern in PATTERNS:
        for suffix in SUFFIXES:
            possible_files.extend(list(path.glob(pattern + suffix)))
    return possible_files


def read_all_valid_budgets(path, path_list, tipologie_skip=None, cache=True):
    """Read valid budget files from a folder."""
    files = find_all_files(path)
    commessa = path.name
    data = data_from_commessa_folder(path)

    # Pre-filter relevant folders once
    commessa_folders = [f for f in path_list if f.name == commessa]
    all_months = sorted(data_from_commessa_folder(folder) for folder in commessa_folders)

    mesi_da_inizio = months_between_dates(data, all_months[0])
    mese, anno = data.month, data.year
    folder_hash = get_folder_hash(path)
    data = f"{anno}-{mese:02d}"

    # Initialize empty DataFrames with correct columns
    loaded = None
    reports = None

    # Process files one by one without accumulating lists
    for file in files:
        fasi, cons_report = read_full_budget_cached(
            file, folder_hash, sum_fasi=False, tipologie_skip=tipologie_skip, cache=cache
        )
        if fasi is not None:
            if loaded is None:
                loaded = fasi
            else:
                # Use DataFrame.append which is more efficient for single DataFrame
                loaded = loaded._append(fasi, ignore_index=True)
        
        if len(cons_report) > 0:
            report_df = pd.DataFrame(cons_report)
            if reports is None:
                reports = report_df
            else:
                reports = reports._append(report_df, ignore_index=True)

    if loaded is None:
        logging.info(f"No file validi in {path}")
        return None, None

    # Add metadata columns
    loaded.loc[:, "commessa"] = commessa
    loaded.loc[:, "mese"] = mese
    loaded.loc[:, "anno"] = anno
    loaded.loc[:, "data"] = data
    loaded.loc[:, "mesi-da-inizio"] = mesi_da_inizio
    loaded.loc[:, "file-hash"] = folder_hash

    if reports is not None:
        reports.loc[:, "commessa"] = commessa
        reports.loc[:, "mese"] = mese
        reports.loc[:, "anno"] = anno
        reports.loc[:, "data"] = data

    return loaded, reports

def load_loop_and_concat(
    folders,
    key_sequence=KEY_SEQUENCE,
    tipologie_fix=None,
    tipologie_skip=None,
    progress_bar=True,
    report_filename=None,
    cache=True,
):
    budgets = []
    reports = []

    if progress_bar:
        wrapper = tqdm
    else:
        wrapper = lambda x: x

    for folder in wrapper(folders):
        logging.info(f"Loading {folder}")
        budget, rep = read_all_valid_budgets(
            folder, folders, tipologie_skip=tipologie_skip, cache=cache
        )
        if rep is not None:
            reports.append(rep)
        
        budgets.append(budget)

    budgets = pd.concat(budgets, axis=0, ignore_index=True)
    budgets = budgets[key_sequence]

    logging.info(f"File consolidato: {len(budgets)} entrate")

    if len(reports) > 0:
        reports = pd.concat(reports, axis=0, ignore_index=True)
        logging.info(f"Report sul file consolidato: {len(reports)} entrate")

    if tipologie_fix is not None:
        fix_tipologie_df(
            budgets,
            tipologie_fix,
            report_filename=report_filename,
        )
        logging.info("Correggo le tipologie...")

    return budgets, reports
