"""Qui sono descritti i parametri di lettura del file, le conversioni delle stringe,
e il formatting dell'output.
"""

# --------------------------------------------------------------------------------------
# Specificazioni foglio di input
# --------------------------------------------------------------------------------------

CODICE_COSTO_COL = 0  # indice colonna con codice costo
TIPOLOGIA_IDX = 1  # indice colonna con tipologie costo
SKIP_COSTI_HEAD = 4  # indice di riga sotto casella "COSTI" a cui leggere gli headers
N_COLONNE = 8  # colonne da tenere nella lettura del file

# Dizionario di colonne chiave del file. Lo definiamo per astrarre il valore specifico
# delle stringhe nel caso debba mutare:
KEY_HEADERS = {
    "costi_start": "COSTI",
    "codice": "codice",
    "units": "u.m.",
    "costo_unit": "costo u.",
    "quantita": "quantita",
    "imp_unit": "imp. unit.",
    "inc_perc": "inc.%",
    "imp_comp": "imp.comp.",
    "tipologia": "tipologia",
    "voce": "voce",
    "fase": "fase",
}

# Alcune celle chiave per la lettura sono state rinominate nei vari file.
# Questo dizionario specifica delle conversioni necessarie:
HEADER_TRASLATIONS_DICT = {
    KEY_HEADERS["costi_start"]: ["DÉPENSES"],
    KEY_HEADERS["codice"]: ["Codice", "Code"],
    KEY_HEADERS["units"]: [],
    KEY_HEADERS["costo_unit"]: ["coût u.", "coît u.", "Costo unit."],
    KEY_HEADERS["quantita"]: ["Quantità", "Quantité", "Quantita"],
    KEY_HEADERS["imp_unit"]: ["mont. unit.", "Prezzo unit."],
    KEY_HEADERS["inc_perc"]: [],
    KEY_HEADERS["imp_comp"]: [
        "mont. comp.",
        "mont. tot.",
        "Costo totale",
        "imp.comp.c.",
    ],
}

EXPECTED_COLS = []

# --------------------------------------------------------------------------------------
# Controlli post-lettura
# --------------------------------------------------------------------------------------
# Tipi attesi dopo corretta lettura del file:
TYPES_MAP = {
    KEY_HEADERS["costo_unit"]: float,
    KEY_HEADERS["quantita"]: float,
    KEY_HEADERS["imp_comp"]: float,
    KEY_HEADERS["codice"]: int,
}

# --------------------------------------------------------------------------------------
# Formattazione output
# --------------------------------------------------------------------------------------
# Valori da aggregare se si somma sulle fasi:
TO_AGGREGATE = [KEY_HEADERS["quantita"], KEY_HEADERS["imp_comp"]]
TO_DROP = [KEY_HEADERS["inc_perc"], KEY_HEADERS["imp_unit"]]

SHEET_COL_SEQ = [
    KEY_HEADERS["codice"],
    KEY_HEADERS["tipologia"],
    KEY_HEADERS["voce"],
    KEY_HEADERS["units"],
    KEY_HEADERS["quantita"],
    KEY_HEADERS["costo_unit"],
    KEY_HEADERS["imp_comp"],
]

SHEET_COL_SEQ_FASE = [
    KEY_HEADERS["fase"],
] + SHEET_COL_SEQ
