import logging
import pickle
import warnings

import numpy as np
import pandas as pd

from pyconsolida.budget_reader_utils import (
    add_tipologia_column,
    crop_costi,
    fix_types,
    fix_voice_consistency,
    get_args_hash,
    get_folder_hash,
    get_repo_version,
    translate_df,
)
from pyconsolida.df_utils import sum_selected_columns
from pyconsolida.sheet_specs import (
    CODICE_COSTO_COL,
    EXCLUDED_FASI,
    HEADERS,
    SHEET_COL_SEQ,
    SHEET_COL_SEQ_FASE,
    TO_AGGREGATE,
)


def _is_valid_costo_code(val):
    """Ritorna True se il valore e' un codice costo valido, False altrimenti."""
    if isinstance(val, int):
        return True
    elif isinstance(val, str):
        try:
            int(val[:-1])
            return True
        except ValueError:
            return False
    return False


def _get_valid_costo_rows(df):
    """Localizza righe con voci costo valide in base al fatto che hanno un intero
    nella colonna codici costo.
    """
    try:
        max_n = np.nonzero(df.iloc[:, CODICE_COSTO_COL].values == "Totale costi")[0][0]
    except IndexError:
        try:
            max_n = np.nonzero(df.iloc[:, CODICE_COSTO_COL].values == "Total dépenses")[
                0
            ][0]
        except IndexError:
            max_n = len(df)  # Tanto verosimilmente questo non e' un foglio di budget
    select = [
        _is_valid_costo_code(cost_id) and i < max_n and i > 0
        for i, cost_id in enumerate(df.iloc[:, CODICE_COSTO_COL])
    ]
    return select


def _read_raw_budget_sheet(df, commessa, fase, tipologie_skip=None):
    """Legge i costi da una pagina di una singola fase del file analisi."""

    # Traduci se necessario:
    df = translate_df(df)

    # Trova l'inizio delle righe costi, e return se non ce ne sono:
    df_costi = crop_costi(df)

    if df_costi is None:
        return

    # Aggiungi colonna con tipologie, trascinando in basso ogni nuovo header tipologia:
    df_costi = add_tipologia_column(
        df_costi, commessa, fase, tipologie_skip=tipologie_skip
    )

    # Seleziona righe con un codice costo valido:
    selection = _get_valid_costo_rows(df_costi)

    voci_costo = df_costi.iloc[selection, :].copy()

    # Makes sure

    if set(voci_costo.columns) != set(SHEET_COL_SEQ):
        # Trova headers mancanti:
        invalid_headers = [not isinstance(a, str) for a in voci_costo.columns]

        # Se manca solo un header si pò provare a correggere:
        if sum(invalid_headers) == 1:
            present_headers = [
                voci_costo.columns[i]
                for i, isinv in enumerate(invalid_headers)
                if not isinv
            ]
            inferred_value = list(set(SHEET_COL_SEQ) - set(present_headers))[0]
            logging.info(
                f"Correggo header mancante in {fase} di {commessa}; assumo {inferred_value}"
            )
            new_headers = [
                inferred_value if isinv else old_col
                for old_col, isinv in zip(voci_costo.columns, invalid_headers)
            ]
            voci_costo.columns = new_headers
        elif sum(invalid_headers) > 1:
            logging.info(
                f"Non trovo gli header attesi {inferred_value} inpyte {commessa}/{fase}"
            )
            return None
            # voci_costo.columns = SHEET_COL_SEQ
    # assert "codice" in voci_costo.columns, f"Header '{header}' not found in {voci_costo.columns}"

    # Rimuovi quantita' uguali a 0
    # Conversione a float e int:
    fix_types(voci_costo)
    voci_costo = voci_costo[voci_costo[HEADERS["quantita"]] > 0]

    return voci_costo


def _read_full_budget(filename, sum_fasi=True, tipologie_skip=None):
    log_messages = []

    # Leggi file:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df = pd.read_excel(filename, sheet_name=None)

    # Cicla su tutti i fogli del file per leggere le fasi:
    all_fasi = []
    for fase, df_fase in df.items():
        if fase not in EXCLUDED_FASI:
            try:
                costi_fase = _read_raw_budget_sheet(
                    df_fase,
                    filename.parent.name,
                    fase,
                    tipologie_skip=tipologie_skip,
                )
            except (KeyError, TypeError, ValueError) as e:
                if "['inc.%'] not found in axis" in str(e):
                    log_messages.append(
                        f"Skipping fase'{fase}' in '{filename}': no costi validi"
                    )
                    costi_fase = None
                else:
                    raise RuntimeError(
                        f"Problem while analyzing fase '{fase}' of file '{filename}'"
                    )
                # to debug you can use notebook.
                # Common problems are: 1. Leftovers on the gray lower part of the sheet; 2. typos replacing labels with eg numbers.from

            if costi_fase is not None:
                if (
                    not sum_fasi
                ):  # ci interessa identita' delle fasi solo se non sommiamo:
                    costi_fase[HEADERS["fase"]] = fase

                all_fasi.append(costi_fase)

    # Aggreghiamo per cantiere per sommare voci costo identiche:
    all_fasi_concat = pd.concat(all_fasi, axis=0, ignore_index=True)

    if len(all_fasi_concat) == 0:
        log_messages.append(rf"Nessuna voce costo valida in file {filename}")

    # Controlla consistenza descrizione voci di costo:
    consistency_report = []
    if len(all_fasi_concat) > 0:
        try:
            all_fasi_concat, consistency_report = fix_voice_consistency(all_fasi_concat)
        except ValueError:
            log_messages.append(f"Errore in fix_voice_consistency per file {filename}")

    # Somma quantita' e importo complessivo:
    if sum_fasi:
        all_fasi_concat = sum_selected_columns(
            all_fasi_concat, HEADERS["codice"], TO_AGGREGATE
        )
        all_fasi_concat = all_fasi_concat[SHEET_COL_SEQ]
    else:
        all_fasi_concat = all_fasi_concat[SHEET_COL_SEQ_FASE]

    return all_fasi_concat, consistency_report, log_messages


def read_full_budget_cached(filename, folder_hash, sum_fasi=True, tipologie_skip=None, cache=True):
    """Read the full budget from a file, using caching."""

    # log_messages.append(f"Re-importo {filename}, no cache per questa versione di script e dati")

    # Define cached filename:
    CACHE_FOLDERNAME = "cached"
    script_hash = get_repo_version()
    args_hash = get_args_hash(sum_fasi=sum_fasi, tipologie_skip=tipologie_skip)

    if cache:
        cached_folder = filename.parent / CACHE_FOLDERNAME
        cached_folder.mkdir(exist_ok=True)
        cached_filename_base = (
            cached_folder
            / f"{filename.stem}_cache_{args_hash}_{folder_hash}_{script_hash}"
        )
        all_fasi_filename = cached_folder / f"{cached_filename_base.stem}.pickle"
        consistency_filename = (
            cached_folder / f"{cached_filename_base.stem}_consistency.pickle"
        )
        log_filename = cached_folder / f"{cached_filename_base.stem}_log.txt"

    # Controlla se c'è già un csv generato con la stessa versione dello script:
    if cache and all(
        [f.exists() for f in [all_fasi_filename, consistency_filename, log_filename]]
    ):
        logging.info(f"Leggo cache da {all_fasi_filename}")
        loaded_from_cache = True
        # Leggi cache:
        all_fasi_concat = pd.read_pickle(all_fasi_filename)
        with open(consistency_filename, "rb") as f:
            consistency_report = pickle.load(f)
        with open(log_filename, "r") as f:
            log_messages = f.readlines()

        # Remove all the other cached files that do not match the current script and folder version:
        for cached_file in cached_folder.glob(
            f"{filename.stem}_cache_{args_hash}*.pickle"
        ):
            if cached_file not in [
                all_fasi_filename,
                consistency_filename,
                log_filename,
            ]:
                cached_file.unlink()

    else:
        logging.info(f"Reading from scratch {filename}")
        all_fasi_concat, consistency_report, log_messages = _read_full_budget(
            filename, sum_fasi, tipologie_skip
        )

        loaded_from_cache = False

    if cache and not loaded_from_cache:
        # Salva con versione dello script e dei file:
        all_fasi_concat.to_pickle(all_fasi_filename)

        pickle.dump(consistency_report, open(consistency_filename, "wb"))
        with open(log_filename, "w") as f:
            for log_message in log_messages:
                f.write(log_message)

    for log_message in log_messages:
        logging.info(log_message)

    return all_fasi_concat, consistency_report
