import pandas as pd


def sum_selected_columns(df, groupby_key, cols_to_sum):
    """Dato un dataframe con chiavi ripetute (eg, codici costo), somma su alcune colonne e prende
    valori statici dalle altre (eg, prezzo unitario o unita' misura).

    Parameters
    ----------
    groupby_key : str
        Colonna sulla quale aggregare.
    cols_to_sum : list of str
        Colonne da sommare.

    Returns
    -------

    """
    # Somma entrate da sommare:
    summed_quantities = df.groupby(groupby_key)[cols_to_sum].sum()
    # Prendi valori statici per tutti gli altri:
    info_quantities = df.groupby(groupby_key).apply(
        take_voce_static_vals, exclude=cols_to_sum
    )

    return pd.concat([summed_quantities, info_quantities], axis=1)


def check_consistence(df, key):
    """Controlla che tutte le stringhe "voce" del dataframe
    siano uguali. Da usare sul dataframe aggregato per codice costo.
    """
    return len(set(df[key])) == 1


def take_voce_static_vals(df, exclude=None):
    """Prende le info statiche (tutte salvo quantita' e importo complessivo)
    relative alla voce costo, selezionando i valori della prima riga del dataframe.
    Da usare sul dataframe aggregato per codice costo.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe.
    exclude : list of str
        Colonne da escludere.

    Returns
    -------

    """
    if len(exclude) > 0:
        df = df.drop(exclude, axis=1)

    return df.iloc[0, :]
