from datetime import datetime

import pandas as pd


def get_multiple_date_intervals(debug_mode=False):
    """Get multiple start-stop date intervals from user input."""

    if debug_mode:
        return [(datetime(2023, 12, 1), datetime(2024, 2, 1))]

    intervals = []
    while True:
        start = input_data("inizio")
        stop = input_data("fine")

        # Validate dates
        if not start < stop:
            raise ValueError(
                "La data di inizio deve essere precedente a quella di fine."
            )
        if not (datetime(2021, 1, 1) <= start <= datetime.now()):
            raise ValueError("La data di inizio deve essere compresa tra 01.2021 e ora")
        if not (datetime(2021, 1, 1) <= stop <= datetime.now()):
            raise ValueError("La data di fine deve essere compresa tra 01.2021 e ora")

        intervals.append((start, stop))

        if input("Vuoi aggiungere un altro intervallo? (s/n): ").lower() != "s":
            break

    return intervals


def input_data(data_name):
    string = input(f"Inserire mese {data_name} in formato MM.AAAA: ")
    month, year = string.split(".")
    return datetime(year=int(year), month=int(month), day=1)


def _sum_repetitive_rows(input_df):
    new_index = ["commessa", "codice", "fase"]
    columns_to_sum = ["quantita", "imp.comp."]

    other_cols = list(set(input_df.columns) - set(new_index + columns_to_sum))

    # ensure we first sum together all rows with identical ["commessa", "codice", "fase"] for columns
    # supporting summing, and we leave the rest as is - it will be filled with the first row
    df_summed = input_df.loc[:, new_index + columns_to_sum]
    df_summed = df_summed.groupby(new_index).sum()

    # for the other columns, we just take the first row:
    df_firstrow = input_df.loc[:, new_index + other_cols]
    df_firstrow = df_firstrow.groupby(new_index).first()
    return pd.concat([df_summed, df_firstrow], axis=1)


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

    def convert_to_datetime(x):
        if pd.isna(x):
            return pd.NaT
        if isinstance(
            x, (pd.Timestamp, type(datetime.now()))
        ):  # Fixed: use concrete datetime type
            return x
        if isinstance(x, str):
            if len(x) == 7:  # YYYY-MM format
                return pd.to_datetime(x + "-01")
            return pd.to_datetime(x)
        return pd.NaT

    # Convert dates
    tabellone_df["data"] = tabellone_df["data"].apply(convert_to_datetime)
    in_range = tabellone_df[
        (tabellone_df["data"] >= t_start_date) & (tabellone_df["data"] <= t_stop_date)
    ]

    min_dates = in_range.groupby("commessa")["data"].min()
    max_dates = in_range.groupby("commessa")["data"].max()

    start_df = in_range[in_range["data"] == in_range["commessa"].map(min_dates)]
    # Ensure we do not subtract eg march 2024 if we are computing delta since december 2023
    # If beginning does not match t_start, the actual starting point is 0:
    start_df = start_df[start_df["data"] == t_start_date]

    start_df = _sum_repetitive_rows(start_df)

    end_df = in_range[in_range["data"] == in_range["commessa"].map(max_dates)]
    end_df = _sum_repetitive_rows(end_df)

    # Align:
    start_al_df, end_al_df = start_df.align(end_df)

    # Prepare infos per tabellone:
    line_info_df = end_al_df.loc[:, ["tipologia", "voce", "u.m.", "costo u."]]
    # Trova indice campi rimasti nan:
    missing_info_idx = line_info_df[
        line_info_df["tipologia"].apply(lambda x: type(x) is not str)
    ].index
    line_info_df.loc[missing_info_idx, :] = start_al_df.loc[
        missing_info_idx, ["tipologia", "voce", "u.m.", "costo u."]
    ]

    # Prepara e calcola delta:
    delta_cols = ["quantita", "imp.comp."]
    all_data_cols = (
        [
            "data",
        ]
        + delta_cols
        + [
            "file-hash",
        ]
    )
    da_df = start_al_df.loc[:, all_data_cols]
    a_df = end_al_df.loc[:, all_data_cols]

    # Fix for FutureWarning: convert to float first, then fill NA values
    da_filled = da_df.loc[:, delta_cols].astype(float).fillna(0)
    a_filled = a_df.loc[:, delta_cols].astype(float).fillna(0)
    delta_df = a_filled - da_filled

    a_df.columns = [f"A: {col}" for col in a_df.columns]
    da_df.columns = [f"DA: {col}" for col in da_df.columns]
    delta_df.columns = [f"DELTA: {col}" for col in delta_df.columns]

    # Target schema
    # tipologia, voce, u.m., costo u., DA:data, quantità, imp.comp; A - data, quantità, imp.com,; DELTA quantità, imp, a hash, da hash

    final_df = pd.concat([line_info_df, da_df, a_df, delta_df], axis=1)
    final_df = final_df[
        [col for col in final_df.columns if "hash" not in col]
        + ["DA: file-hash", "A: file-hash"]
    ]

    return final_df.reset_index()
