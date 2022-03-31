"""Qui sono descritti i parametri di lettura del file, le conversioni delle stringe,
e il formatting dell'output.
"""

# --------------------------------------------------------------------------------------
# Specificazioni foglio di input
# --------------------------------------------------------------------------------------

CODICE_COSTO_COL = 0  # indice colonna con codice costo
SKIP_FOR_HEADERS = 4  # indice di riga sotto casella "COSTI" a cui leggere gli headers
N_COLONNE = 8  # colonne da tenere nella lettura del file

# Alcune celle chiave per la lettura sono state rinominate nei vari file.
# Questo dizionario specifica delle conversioni necessarie:
HEADER_TRASLATIONS_DICT = {
    "COSTI": ["DÉPENSES"],
    "codice": ["Codice", "Code"],
    "u.m.": [],
    "costo u.": ["coût u.", "coît u.", "Costo unit."],
    "quantita": ["Quantità", "Quantité", "Quantita"],
    "imp. unit.": ["mont. unit.", "Prezzo unit."],
    "inc.%": [],
    "imp.comp.": ["mont. comp.", "mont. tot.", "Costo totale", "imp.comp.c."],
}

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


# --------------------------------------------------------------------------------------
# Controlli post-lettura
# --------------------------------------------------------------------------------------
# Tipi attesi dopo corretta lettura del file:
TYPES_MAP = {"costo u.": float, "quantita": float, "imp.comp.": float, "codice": int}

# --------------------------------------------------------------------------------------
# Formattazione output
# --------------------------------------------------------------------------------------
# Valori da aggregare se si somma sulle fasi:
TO_AGGREGATE = ["quantita", "imp.comp."]
TO_DROP = ["inc.%", "imp. unit."]
