"""Qui sono descritti i parametri di lettura del file, le conversioni delle stringe,
e il formatting dell'output.
"""

# --------------------------------------------------------------------------------------
# Specificazioni foglio di input
# --------------------------------------------------------------------------------------
PATTERNS = [
    "*nalis*",
    "*RO-RO*",
    "*ACC.QUADRO*",
    "*SPE_GENE*",
    "*SPE_BRANCH*",
    "*NALIS*",
]

SUFFIXES = [".xls", ".xlsx", ".xlsm"]


CODICE_COSTO_COL = 0  # indice colonna con codice costo
TIPOLOGIA_IDX = 1  # indice colonna con tipologie costo
SKIP_COSTI_HEAD = 4  # indice di riga sotto casella "COSTI" a cui leggere gli headers
N_COLONNE = 8  # colonne da tenere nella lettura del file

# Dizionario di colonne chiave del file. Lo definiamo per astrarre il valore specifico
# delle stringhe nel caso debba mutare:
HEADERS = {
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
    HEADERS["costi_start"]: ["DÉPENSES"],
    HEADERS["codice"]: ["Codice", "Code"],
    HEADERS["units"]: [],
    HEADERS["costo_unit"]: ["coût u.", "coît u.", "Costo unit.", "costou."],
    HEADERS["quantita"]: ["Quantità", "Quantité", "Quantita"],
    HEADERS["imp_unit"]: ["mont. unit.", "Prezzo unit."],
    HEADERS["inc_perc"]: [],
    HEADERS["imp_comp"]: [
        "mont. comp.",
        "mont. tot.",
        "Costo totale",
        "imp.comp.c.",
        "imp.comp. c.",
    ],
}

EXPECTED_COLS = []

EXCLUDED_FASI = ["0-SIT&PROG(2022-24)_", "0-SIT&PROG(2022-24)_prova"]

WORKS_TO_EXCLUDE = ["4004", "9981", "1360", "1445"]

# --------------------------------------------------------------------------------------
# Controlli post-lettura
# --------------------------------------------------------------------------------------
# Tipi attesi dopo corretta lettura del file:
TYPES_MAP = {
    HEADERS["costo_unit"]: float,
    HEADERS["quantita"]: float,
    HEADERS["imp_comp"]: float,
    HEADERS["imp_unit"]: float,
    HEADERS["codice"]: int,
}

# --------------------------------------------------------------------------------------
# Formattazione output
# --------------------------------------------------------------------------------------
# Valori da aggregare se si somma sulle fasi:
TO_AGGREGATE = [HEADERS["quantita"], HEADERS["imp_comp"]]
TO_DROP = [HEADERS["inc_perc"]]  # , HEADERS["imp_unit"]]

SHEET_COL_SEQ = [
    HEADERS["codice"],
    HEADERS["tipologia"],
    HEADERS["voce"],
    HEADERS["costo_unit"],
    HEADERS["units"],
    HEADERS["quantita"],
    HEADERS["imp_unit"],
    HEADERS["imp_comp"],
]

SHEET_COL_SEQ_FASE = [
    HEADERS["fase"],
] + SHEET_COL_SEQ

# sequence of keys in the final table:
KEY_SEQUENCE = [
    "commessa",
    "fase",
    "anno",
    "mese",
    "data",
    "mesi-da-inizio",
    "codice",
    "tipologia",
    "voce",
    "costo u.",
    "u.m.",
    "quantita",
    "imp. unit.",
    "imp.comp.",
    "file-hash",
]
