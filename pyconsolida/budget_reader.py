import pandas as pd
from pyconsolida.budget_reader_utils import fix_types, translate_df, add_tipologia_column, select_costi
from pyconsolida.df_utils import check_consistence, sum_selected_columns

N_COLONNE = 8
TO_DROP = ["inc.%", "imp. unit."]


def read_raw_budget_sheet(df):
    """Legge i costi da una pagina di una singola fase del file analisi.
    """

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

        if not sum_fasi:  # ci interessa identita' delle fasi solo se non sommiamo:
            costi_fase["fase"] = fase

        all_fasi.append(costi_fase)

    # Aggreghiamo per cantiere per sommare voci costo identiche:
    all_fasi_concat = pd.concat(all_fasi, axis=0, ignore_index=True)

    # Controlla consistenza descrizione voci di costo:
    is_consistent = all_fasi_concat.groupby("codice").apply(check_consistence, "voce")

    if not is_consistent.all():
        print(f"descrizione voce costo non univoca per {is_consistent[~is_consistent]} nel file {filename}")

    # Somma quantita' e importo complessivo:
    if sum_fasi:
        all_fasi_concat = sum_selected_columns(all_fasi_concat, "codice", ["quantita", "imp.comp."])

    return all_fasi_concat