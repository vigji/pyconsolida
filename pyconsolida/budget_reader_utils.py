import numpy as np

from pyconsolida.sheet_specs import HEADER_TRASLATIONS_DICT, TYPES_MAP


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


def select_costi(df):
    """Seleziona righe dello spreadsheet che si riferiscono a costi.
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
        start_costi = np.argwhere(df.values == "COSTI")[0, 0]
    except IndexError:
        return

    return df.iloc[start_costi:, :].copy()


def is_tipologia_header(row):
    """Controlla se la riga corrente e' una voce o l'header di una
    nuova tipologia di voci ("Personale", "Noli", etc).
    """
    if type(row.iloc[1]) is not str:
        return False

    if type(row.iloc[2]) is str:
        if row.iloc[2] != "u.m.":
            return False
    else:
        if not np.isnan(row.iloc[2]):
            return False

    return True


def add_tipologia_column(df):
    """Aggiunge una colonna con la tipologia di costo (manodopera, materiale d'opera, etc.).

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Con la colonna "tipologia" aggiunta

    """
    current_tipologia = ""
    df = df.copy()  # work on a copy

    df["tipologia"] = ""
    for row_i, row in enumerate(df.index):
        if is_tipologia_header(df.iloc[row_i, :]):
            current_tipologia = df.iloc[row_i, 1]

        df.loc[row, "tipologia"] = current_tipologia

    return df
