import numpy as np

from pyconsolida.sheet_specs import (
    HEADER_TRASLATIONS_DICT,
    HEADERS,
    N_COLONNE,
    SKIP_COSTI_HEAD,
    TIPOLOGIA_IDX,
    TO_DROP,
    TYPES_MAP,
)


def translate_df(df):
    """Traduce le parti essenziali del file se necessario, come per la Francia,
    o gli eventuali header cambiati.
    """

    for key, vals in HEADER_TRASLATIONS_DICT.items():
        for val in vals:
            df = df.where(df != val, key)
    return df


def fix_types(df):
    """Assicura consistenza dei types delle colonne.
    Modifica il dataframe in input!
    """
    for k, typ in TYPES_MAP.items():
        df.loc[:, k] = df.loc[:, k].astype(typ)


def crop_costi(df):
    """Seleziona righe e colonne dello spreadsheet che si riferiscono a costi.
    Se il foglio è vuoto o non ha costi validi, return None - alcuni file hanno
    fogli vuoti tra le fasi.
    """
    # Foglio vuoto:
    if len(df) == 0:
        return

    # Foglio non vuoto ma nessuna voce valida (letto con nans):
    if df.values.dtype == np.float64:
        return

    try:
        # Trova COSTI e salta un certo numero di righe fissato
        start_costi = (
            np.argwhere(df.values == HEADERS["costi_start"])[0, 0] + SKIP_COSTI_HEAD
        )
    except IndexError:
        return

    # Setta la prima riga come header:
    cropped_df = df.iloc[start_costi:, :N_COLONNE].copy()

    # Trova headers delle colonne nella prima riga:
    colonne = list(cropped_df.iloc[0, :])
    # Per come è fatto il file questa cella ha una tipologia anzichè un header:
    colonne[1] = HEADERS["voce"]

    cropped_df.columns = colonne

    # Rimuovi colonne indesiderate
    cropped_df = cropped_df.drop(TO_DROP, axis=1)

    return cropped_df


def _is_tipologia_header(row):
    """Controlla se la riga corrente e' una voce o l'header di una
    nuova tipologia di voci ("Personale", "Noli", etc).
    """
    if type(row.iloc[1]) is not str:
        return False

    if type(row.iloc[2]) is str:
        if row.iloc[2] != HEADERS["units"]:
            return False
    else:
        if not np.isnan(row.iloc[2]):
            return False

    return True


def add_tipologia_column(df):
    """Aggiunge una colonna con la tipologia di costo (manodopera, materiale d'opera,
    etc.).

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Con la colonna "tipologia" aggiunta

    """
    df = df.copy()  # lavora in copia

    df[HEADERS["tipologia"]] = ""

    current_tipologia = ""  # sovrascriveremo il valore nel loop
    for row_i, row in enumerate(df.index):
        # Se c'è una nuova tipologia, aggiorna current_tipologia:
        if _is_tipologia_header(df.iloc[row_i, :]):
            current_tipologia = df.iloc[row_i, TIPOLOGIA_IDX]

        df.loc[row, HEADERS["tipologia"]] = current_tipologia

    return df
