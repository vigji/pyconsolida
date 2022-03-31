import pandas as pd

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


def _get_valid_costo_rows(df):
    """Localizza righe con voci costo valide in base al fatto che hanno un intero
    nella colonna codici costo.
    """
    return list(map(lambda n: isinstance(n, int), df.iloc[:, CODICE_COSTO_COL]))


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
    voci_costo = voci_costo[voci_costo[HEADERS["quantita"]] > 0]

    # Conversione a float e int:
    fix_types(voci_costo)

    return voci_costo


def read_full_budget(filename, sum_fasi=True):
    # Leggi file:
    df = pd.read_excel(filename, sheet_name=None)

    # Cicla su tutti i fogli del file per leggere le fasi:
    all_fasi = []
    for fase, df_fase in df.items():
        costi_fase = _read_raw_budget_sheet(df_fase)

        if costi_fase is not None:
            if not sum_fasi:  # ci interessa identita' delle fasi solo se non sommiamo:
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
