import pandas as pd
from datetime import datetime


def input_data(data_name):
    string = input(f"Inserire mese {data_name} in formato MM.AAAA: ")
    month, year = string.split(".")
    return datetime(year=int(year), 
                    month=int(month),
                    day=1)


def get_tabellone_delta(tabellone_df, t_start_date, t_stop_date):
    """Date due date di inizio e di fine e il tabellone con tutto il dataset, ritorna
    il delta di costi tra le due date.

    Parameters
    ----------
    tabellone : pd.DataFrame
        Il tabellone con tutti i dati.
    t_start_date : datetime
        Data di inizio.
    t_stop_date : datetime
        Data di fine.
    
    Returns
    -------
    pd.DataFrame
        Il delta di costi tra le due date.
    """
    tabellone_df["data"] = tabellone_df["data"].apply(lambda x: x + "-01")
    tabellone_df["data"] = pd.to_datetime(tabellone_df["data"])

    in_range = tabellone_df[(tabellone_df["data"] >= t_start_date) & (tabellone_df["data"] <= t_stop_date)]

    min_dates = in_range.groupby("commessa")["data"].min()
    max_dates = in_range.groupby("commessa")["data"].max()

    new_index = ["commessa", "codice", "fase"]
    start_df = in_range[in_range["data"] == in_range["commessa"].map(min_dates)].set_index(new_index)
    end_df = in_range[in_range["data"] == in_range["commessa"].map(max_dates)].set_index(new_index)

    # Align:
    start_al_df, end_al_df = start_df.align(end_df)

    # Prepare infos per tabellone:
    line_info_df = end_al_df.loc[:, ["tipologia", "voce", "u.m.", "costo u."]]
    # Trova indice campi rimasti nan:
    missing_info_idx = line_info_df[line_info_df["tipologia"].apply(lambda x: type(x) is not str)].index
    line_info_df.loc[missing_info_idx, :] = start_al_df.loc[missing_info_idx, ["tipologia", "voce", "u.m.", "costo u."]]

    # Prepara e calcola delta:
    delta_cols = ["quantita", "imp.comp."]
    all_data_cols = ["data",] + delta_cols + ["file-hash",]
    da_df = start_al_df.loc[:, all_data_cols]
    a_df = end_al_df.loc[:, all_data_cols]

    delta_df = a_df.loc[:, delta_cols].fillna(0) - da_df.loc[:, delta_cols].fillna(0)

    a_df.columns = [f"A: {col}" for col in a_df.columns]
    da_df.columns = [f"DA: {col}" for col in da_df.columns]
    delta_df.columns = [f"DELTA: {col}" for col in delta_df.columns]

    # Target schema
    # tipologia, voce, u.m., costo u., DA:data, quantità, imp.comp; A - data, quantità, imp.com,; DELTA quantità, imp, a hash, da hash

    final_df = pd.concat([line_info_df, da_df, a_df, delta_df], axis=1)
    final_df = final_df[[col for col in final_df.columns if "hash" not in col] + ['DA: file-hash', 'A: file-hash']]

    return final_df.reset_index()
