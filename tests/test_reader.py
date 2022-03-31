import flammkuchen as fl
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from pyconsolida.budget_reader import read_full_budget
from pyconsolida.posthoc_fix_utils import fix_tipologie_df


@pytest.mark.parametrize("sum_fasi", [True, False])
def test_budget_reader(assets_folder, sum_fasi):
    expected = fl.load(assets_folder / "expected.h5")

    data_path = assets_folder / "test_raw_sheet.xls"

    budget, rep = read_full_budget(data_path, sum_fasi=sum_fasi)
    assert_frame_equal(expected[f"sum_{str(sum_fasi)}"], budget)


def test_fix_tipologie(assets_folder):
    # TODO currently working only without summing
    budget = fl.load(assets_folder / "expected.h5", "/sum_False")
    tipologie_fix = pd.read_excel(assets_folder / "tipologie_fix.xlsx")

    fix_tipologie_df(budget, tipologie_fix)
