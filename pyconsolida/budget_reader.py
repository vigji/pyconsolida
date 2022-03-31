import numpy as np
import pandas as pd

from pyconsolida.budget_reader_utils import (
    add_tipologia_column,
    fix_types,
    select_costi,
    translate_df,
)
from pyconsolida.df_utils import sum_selected_columns

N_COLONNE = 8
TO_DROP = ["inc.%", "imp. unit."]


def _aggregate(df):
    df_out = df.iloc[0, :]
    if len(df) > 1:
        # print(df.loc[:, ["quantita", "imp.comp."]].sum())
        df_out[["quantita", "imp.comp."]] = df.loc[:, ["quantita", "imp.comp."]].sum()
    return df_out


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


def read_raw_budget_sheet(df):
    """Legge i costi da una pagina di una singola fase del file analisi."""

    # Traduci se necessario:
    df = translate_df(df)

    # Trova l'inizio delle righe costi, e return se non ce ne sono:
    df_costi = select_costi(df)

    if df_costi is None:
        return

    # Aggiungi colonna con tipologie, trascinando in basso ogni nuovo header tipologia:
    df_costi = add_tipologia_column(df_costi)

    # Seleziona righe con un codice costo valido:
    selection = list(map(lambda n: isinstance(n, int), df_costi.iloc[:, 0]))
    voci_costo = df_costi.iloc[selection, :N_COLONNE].copy()

    # Rinomina colonne:
    colonne = df_costi.iloc[4, :N_COLONNE].values
    colonne[1] = "voce"
    voci_costo.columns = colonne

    # Aggiungi categoria, (fase) e cantiere:
    voci_costo["tipologia"] = df_costi.loc[selection, "tipologia"].copy()

    # Qualche pulizia aggiuntiva:
    voci_costo = voci_costo[voci_costo["quantita"] > 0]  # rimuovi quantita' uguali a 0
    voci_costo = voci_costo.drop(TO_DROP, axis=1)  # rimuovi colonne indesiderate

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
        all_fasi_concat = sum_selected_columns(
            all_fasi_concat, "codice", ["quantita", "imp.comp."]
        )

    return all_fasi_concat, consistency_report
