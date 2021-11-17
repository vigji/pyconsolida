from numba import njit
from numba.core.errors import NumbaPendingDeprecationWarning
import warnings
import numpy as np
import pandas as pd

warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)


def fix_tipologie_df(input_df, tipologie_fix_df, report_filename=None):
    # Make everything lowercase and replace nans with not-searchable string:
    to_change = _isinlist(format_to_check(input_df["voce"]), format_to_check(input_df["tipologia"]),
                          format_check(tipologie_fix_df["se contiene"]), format_check(tipologie_fix_df["e non contiene"]),
                          format_check(tipologie_fix_df["da"]))

    # Ensures that no ambiguous category conversions are defined:
    all_matches = np.argwhere(to_change)
    duplex_conversions = np.argwhere(np.sum(to_change, 1) > 1).flatten()

    for i in duplex_conversions:
        possible_matches = all_matches[all_matches[:, 0] == i, 1]
        if len(set(tipologie_fix_df["a"].values[possible_matches])) > 1:
            print("ambiguous tipologia change defined for:"),
            print(tipologie_fix_df.iloc[possible_matches, :].to_markdown())
            raise ValueError("Ambiguous tipologia change defined!")

    # Once this is safe, we can just use the matches interchangably:
    indexes_to_change = np.argwhere(to_change)

    if report_filename is not None:
        # Create and save dataframe reporting all changes that happened:
        report_df = pd.DataFrame(dict(fix_match_n=indexes_to_change[:, 1],
                                      da=tipologie_fix_df.loc[indexes_to_change[:, 1], "da"],
                                      a=tipologie_fix_df.loc[indexes_to_change[:, 1], "a"]))
        report_df = pd.concat([input_df.loc[indexes_to_change[:, 0]].reset_index(), report_df.reset_index()],
                              axis=1)

        report_df.to_excel(report_filename)

    # Fix inplace tipologia in the dataframe:
    prev = indexes_to_change[0, 0]
    for i, j in indexes_to_change:
        # sanity check - would not work because of duplicated vals, hence the prev:
        if i != prev:
            assert input_df.loc[i, "tipologia"] == tipologie_fix_df.loc[j, "da"]
        input_df.loc[i, "tipologia"] = tipologie_fix_df.loc[j, "a"]

        prev = i


def isnan(val):
    if type(val) == str:
        return False
    else:
        return np.isnan(val)


def replacenan(val):
    if isnan(val):
        return "!@#$#$^"
    else:
        return val


def format_check(check_list):
    return tuple([replacenan(i).lower() for i in check_list])


def format_to_check(check_list):
    return list([replacenan(i).lower() for i in check_list])


@njit
def _isinlist(voci, tipologie, check_list, exclude_list, tipologie_list):
    """Fast match of occourrences satifying a condition.

    Parameters
    ----------
    voci
    tipologie
    check_list
    exclude_list
    tipologie_list

    Returns
    -------

    """
    matches_table = np.full((len(voci), len(check_list)), False)

    for i in range(len(voci)):
        voce_to_check = voci[i]
        for j in range(len(check_list)):
            if check_list[j] in voce_to_check and exclude_list[j] not in voce_to_check and tipologie[i] == \
                    tipologie_list[j]:
                matches_table[i, j] = True
    return matches_table