import flammkuchen as fl
from pandas.testing import assert_frame_equal

from pyconsolida.budget_reader import read_full_budget


def test_budget_reader(assets_folder):
    expected = fl.load(assets_folder / "expected.h5")

    data_path = assets_folder / "test_raw_sheet.xls"

    for sum_fasi in [False, True]:
        budget, rep = read_full_budget(data_path, sum_fasi=sum_fasi)
        assert_frame_equal(expected[f"sum_{str(sum_fasi)}"], budget)
