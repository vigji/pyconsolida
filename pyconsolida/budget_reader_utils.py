import numpy as np

# Alcune celle chiave per la lettura sono state rinominate nei vari file.
# Questo dizionario specifica delle conversioni necessarie
TRASLATIONS_MAP = {
    "Quantità": "quantita",
    "Quantité": "quantita",
    "Quantita": "quantita",
    "Codice": "codice",
    "Code": "codice",
    "DÉPENSES": "COSTI",
    "coût u.": "costo u.",
    "coît u.": "costo u.",
    "Costo unit.": "costo u.",
    "mont. unit.": "imp. unit.",
    "Prezzo unit.": "imp. unit.",
    "mont. comp.": "imp.comp.",
    "mont. tot.": "imp.comp.",
    "Costo totale": "imp.comp.",
    "imp.comp.c.": "imp.comp.",
}

# Tipi attesi dopo corretta lettura del file:
TYPES_MAP = {"costo u.": float, "quantita": float, "imp.comp.": float, "codice": int}


def translate_df(df):
    """Traduce le parti essenziali del file se necessario, come per la Francia."""

    # Sostituisci tutte le entrate che hanno una chiave nel dizionario:
    for key, val in TRASLATIONS_MAP.items():
        df = df.where(df != key, val)
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
    if len(df) == 0:  # foglio vuoto
        return
    if df.values.dtype == np.float64:  # foglio non vuoto ma nessuna voce valida
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
