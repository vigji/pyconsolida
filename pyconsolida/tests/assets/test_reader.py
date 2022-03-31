import flammkuchen as fl
import pytest
from pandas.testing import assert_frame_equal

from pyconsolida.budget_reader import read_full_budget


@pytest.mark.parametrize("sum_fasi", [True, False])
def test_budget_reader(assets_folder, sum_fasi):
    expected = fl.load(assets_folder / "expected.h5")

    data_path = assets_folder / "test_raw_sheet.xls"

    budget, rep = read_full_budget(data_path, sum_fasi=sum_fasi)
    assert_frame_equal(expected[f"sum_{str(sum_fasi)}"], budget)
