import logging
import warnings

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
    """Ensures consistency of data types of all columns.
    It changes the input inplace!!
    """

    for k, typ in TYPES_MAP.items():
        if k == HEADERS["codice"]:
            # ogni tanto qualcuno aggiunge carattere in fondo a numero codice costo:
            df.loc[:, k] = df.loc[:, k].apply(fix_codice_costo_alphanum)
        if k == HEADERS["costo_unit"]:
            df.loc[:, k] = df.loc[:, k].apply(
                lambda x: (
                    typ(x.replace(" ", "").replace(",", "."))
                    if type(x) is str
                    else typ(x)
                )
            )
        else:
            df.loc[:, k] = df.loc[:, k].astype(typ)


def fix_codice_costo_alphanum(val):
    try:
        return int(val)
    except ValueError:
        return int(val[:-1])


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
        costi_cells = np.argwhere(df.values == HEADERS["costi_start"])
        if (
            costi_cells.shape[0] > 1
        ):  # Found at least 1 funny case of a duplicated COSTI row, invisible in the xls file
            logging.warning("Buffa duplicazione fantasma casella COSTI")
        start_costi = costi_cells[-1, 0]
        start_costi += SKIP_COSTI_HEAD  # skip predefined number of rows from "COSTI"
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


def _is_tipologia_header(row, commessa, fase, tipologie_skip=None):
    """Controlla se la riga corrente e' una voce o l'header di una
    nuova tipologia di voci ("Personale", "Noli", etc).

    Siccome alcune correzione sono fatte su fogli specifici, per ora
    serve propagare fino a qui l'info su commessa e fase.
    """
    if type(row.iloc[1]) is not str:
        return False

    try:
        int_commessa = int(commessa)
    except ValueError:
        int_commessa = int(commessa[:4])  # Alcune cartelle hanno XXX-Preventivo

    # Esclusione a mano di alcuni casi specifici in cui pseudo headers di
    # tipologia sono a uso interno commessa e quindi da evitare::
    if tipologie_skip is not None:
        conditions_matched = sum(
            (tipologie_skip["tipologia"] == row.iloc[1])
            & (tipologie_skip["commessa"] == int_commessa)
            & (tipologie_skip["fase"] == fase)
        )

        if conditions_matched:
            logging.warning(f"Ignoro header '{row.iloc[1]}' in  {commessa}/{fase}")
            return False

    if type(row.iloc[2]) is str:
        if row.iloc[2] != HEADERS["units"]:
            return False
    else:
        if not np.isnan(row.iloc[2]):
            return False

    return True


def add_tipologia_column(df, commessa, fase, tipologie_skip=None):
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
        if _is_tipologia_header(
            df.iloc[row_i, :], commessa, fase, tipologie_skip=tipologie_skip
        ):
            current_tipologia = df.iloc[row_i, TIPOLOGIA_IDX]

        df.loc[row, HEADERS["tipologia"]] = current_tipologia

    return df


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

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Boolean Series key will be reindexed to match DataFrame index.",
        )
        consistence_report = consistence_report[
            consistence_report.apply(lambda x: type(x) is not float)
        ]

    # Fix inconsistent voices:
    codice_mapping = df.groupby("codice").apply(_map_consistent_voce, "voce")
    # try:
    df["voce"] = df["codice"].map(codice_mapping)
    # except ValueError:

    return df, consistence_report
