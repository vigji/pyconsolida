import pandas as pd
import numpy as np
import logging

from pyconsolida.budget_reader_utils import (
    add_tipologia_column,
    crop_costi,
    fix_types,
    fix_voice_consistency,
    translate_df,
)
from pyconsolida.df_utils import sum_selected_columns
from pyconsolida.sheet_specs import (
    CODICE_COSTO_COL,
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
            max_n = np.nonzero(df.iloc[:, CODICE_COSTO_COL].values == "Total dépenses")[0][0]
        except IndexError:
            max_n = len(df)  # Tanto verosimilmente questo non e' un foglio di budget
    select = [_is_valid_costo_code(cost_id) and i < max_n for i, cost_id in enumerate(df.iloc[:, CODICE_COSTO_COL])]
    return select


def _read_raw_budget_sheet(df):
    """Legge i costi da una pagina di una singola fase del file analisi."""

    # Traduci se necessario:
    df = translate_df(df)

    # Trova l'inizio delle righe costi, e return se non ce ne sono:
    df_costi = crop_costi(df)

    if df_costi is None:
        return

    # Aggiungi colonna con tipologie, trascinando in basso ogni nuovo header tipologia:
    df_costi = add_tipologia_column(df_costi)

    # Seleziona righe con un codice costo valido:
    selection = _get_valid_costo_rows(df_costi)

    voci_costo = df_costi.iloc[selection, :].copy()

    # Rimuovi quantita' uguali a 0
    # Conversione a float e int:
    fix_types(voci_costo)
    voci_costo = voci_costo[voci_costo[HEADERS["quantita"]] > 0]

    return voci_costo


def read_full_budget(filename, sum_fasi=True):
    # Leggi file:
    df = pd.read_excel(filename, sheet_name=None)

    # Cicla su tutti i fogli del file per leggere le fasi:
    all_fasi = []
    for fase, df_fase in df.items():
        if fase not in ["0-SIT&PROG(2022-24)_", "0-SIT&PROG(2022-24)_prova"]:
            try:
                costi_fase = _read_raw_budget_sheet(df_fase)
            except (KeyError, TypeError, ValueError) as e:
                if "['inc.%'] not found in axis" in str(e):
                    logging.info(
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
        raise ValueError(rf"Nessuna voce costo valida in file {filename}")

    # Controlla consistenza descrizione voci di costo:
    all_fasi_concat, consistency_report = fix_voice_consistency(all_fasi_concat)

    # Somma quantita' e importo complessivo:
    if sum_fasi:
        all_fasi_concat = sum_selected_columns(
            all_fasi_concat, HEADERS["codice"], TO_AGGREGATE
        )
        all_fasi_concat = all_fasi_concat[SHEET_COL_SEQ]
    else:
        all_fasi_concat = all_fasi_concat[SHEET_COL_SEQ_FASE]

    return all_fasi_concat, consistency_report
