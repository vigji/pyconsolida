import numpy as np
import pandas as pd

from pyconsolida.budget_reader_utils import (
    add_tipologia_column,
    fix_types,
    crop_costi,
    translate_df,
)
from pyconsolida.df_utils import sum_selected_columns
from pyconsolida.sheet_specs import (
    CODICE_COSTO_COL,
    N_COLONNE,
    SKIP_COSTI_HEAD,
    TO_AGGREGATE,
    TO_DROP, SHEET_COL_SEQ_FASE, SHEET_COL_SEQ
)


def _diagnose_consistence(df, key):
    if not len(set(df[key])) == 1:
        return set(df[key])
    else:
        return np.nan


def _map_consistent_voce(df, key):
    return df[key].values[0]


def fix_voice_consistency(df):
    # Create report of inconsistent voices:
    consistence_report = df.groupby("codice").apply(_diagnose_consistence, "voce")
    consistence_report = consistence_report[
        consistence_report.apply(lambda x: type(x) is not float)
    ]

    # Fix inconsistent voices:
    codice_mapping = df.groupby("codice").apply(_map_consistent_voce, "voce")
    df["voce"] = df["codice"].map(codice_mapping)

    return df, consistence_report

def _get_valid_costo_row(df):
    """Localizza righe con voci costo valide in base al fatto che hanno un intero
    nella colonna codici costo.
    """
    return list(
        map(lambda n: isinstance(n, int), df.iloc[:, CODICE_COSTO_COL])
    )

def read_raw_budget_sheet(df):
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
    selection = _get_valid_costo_row(df_costi)

    voci_costo = df_costi.iloc[selection, :].copy()

    # Trova headers delle colonne a un certo indice dalla voce "COSTI":
    colonne = list(df_costi.columns)

    # per come è fatto il file questa cella ha una tipologia anzichè un header:
    colonne[1] = "voce"
    voci_costo.columns = colonne

    # Qualche pulizia aggiuntiva:
    voci_costo = voci_costo[voci_costo["quantita"] > 0]  # rimuovi quantita' uguali a 0

    # Conversione a float e int:
    fix_types(voci_costo)

    return voci_costo


def read_full_budget(filename, sum_fasi=True):
    # Leggi file:
    df = pd.read_excel(filename, sheet_name=None)

    # Cicla su tutti i fogli del file per leggere le fasi:
    all_fasi = []
    for fase, df_fase in df.items():
        costi_fase = read_raw_budget_sheet(df_fase)
        # assert "codice" in costi_fase.columns

        if costi_fase is not None:
            if not sum_fasi:  # ci interessa identita' delle fasi solo se non sommiamo:
                costi_fase["fase"] = fase

            all_fasi.append(costi_fase)

    # Aggreghiamo per cantiere per sommare voci costo identiche:
    all_fasi_concat = pd.concat(all_fasi, axis=0, ignore_index=True)

    if len(all_fasi_concat) == 0:
        raise ValueError(rf"Nessuna voce costo valida in file {filename}")

    # Controlla consistenza descrizione voci di costo:
    all_fasi_concat, consistency_report = fix_voice_consistency(all_fasi_concat)
    if len(consistency_report) > 0:
        print(consistency_report)

    # Somma quantita' e importo complessivo:
    if sum_fasi:
        all_fasi_concat = sum_selected_columns(all_fasi_concat, "codice", TO_AGGREGATE)
        all_fasi_concat = all_fasi_concat[SHEET_COL_SEQ]
    else:
        all_fasi_concat = all_fasi_concat[SHEET_COL_SEQ_FASE]

    return all_fasi_concat, consistency_report
