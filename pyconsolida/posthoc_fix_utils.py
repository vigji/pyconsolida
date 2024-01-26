import warnings

import numpy as np
import pandas as pd
from numba import njit
from numba.core.errors import NumbaPendingDeprecationWarning

warnings.simplefilter("ignore", category=NumbaPendingDeprecationWarning)


def fix_tipologie_df(input_df, tipologie_fix_df, report_filename=None):
    # Make everything lowercase and replace nans with not-searchable string:
    to_change = isinlist(input_df, tipologie_fix_df)

    # Ensures that no ambiguous category conversions are defined:
    check_consistency_of_matches(
        to_change, input_df["voce"], tipologie_fix_df, mapped_label_key="a"
    )

    # Once this is safe, we can just use the matches interchangably:
    indexes_to_change = np.argwhere(to_change)

    if report_filename is not None:
        # Create and save dataframe reporting all changes that happened:
        report_df = pd.DataFrame(
            dict(
                fix_match_n=indexes_to_change[:, 1],
                da=tipologie_fix_df.loc[indexes_to_change[:, 1], "da"],
                a=tipologie_fix_df.loc[indexes_to_change[:, 1], "a"],
            )
        )
        report_df = pd.concat(
            [
                input_df.loc[indexes_to_change[:, 0]].reset_index(),
                report_df.reset_index(),
            ],
            axis=1,
        )

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
    if isinstance(val, str):
        return False
    else:
        return np.isnan(val)


def replacenan(val):
    if isnan(val):
        return "!@#$#$^"
    else:
        return str(val)  # ensure this is string


def format_check(check_list):
    return tuple([replacenan(i).lower() for i in check_list])


def format_to_check(check_list):
    # print(check_list)
    # try:
    return list([replacenan(i).lower() for i in check_list])
    # except AttributeError:


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
            # handle the option of multiple exclusion criteria separated by divisor char:
            negative_check = np.array(
                [~(s in voce_to_check) for s in exclude_list[j].split(";")]
            ).all()
            if (
                check_list[j] in voce_to_check
                and negative_check
                and tipologie[i] == tipologie_list[j]
            ):
                matches_table[i, j] = True
    return matches_table


def isinlist(
    input_df,
    tipologie_fix_df,
    voce_key="voce",
    tipologia_key="tipologia",
    se_contiene_key="se contiene",
    se_non_contiene_key="e non contiene",
    se_tipologia_key="da",
):
    # print(tipologie_fix_df)
    return _isinlist(
        format_to_check(input_df[voce_key]),
        format_to_check(input_df[tipologia_key]),
        format_check(tipologie_fix_df[se_contiene_key]),
        format_check(tipologie_fix_df[se_non_contiene_key]),
        format_check(tipologie_fix_df[se_tipologia_key]),
    )


def check_consistency_of_matches(
    matches_mat, tested_series, condition_df, mapped_label_key, raise_error=True
):
    # Ensures that no ambiguous category conversions are defined:
    all_matches = np.argwhere(matches_mat)
    duplex_conversions = np.argwhere(np.sum(matches_mat, 1) > 1).flatten()

    for i in duplex_conversions:
        possible_matches = all_matches[all_matches[:, 0] == i, :]
        if len(set(condition_df[mapped_label_key].values[possible_matches[:, 1]])) > 1:
            print("ambiguous match change defined for: "),
            print(tested_series.loc[possible_matches[0, 0]])
            print(condition_df.iloc[possible_matches[:, 1], :].to_markdown())
            if raise_error:
                raise ValueError("Ambiguous change defined!")
