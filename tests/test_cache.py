import time

import pytest

from pyconsolida.budget_reader import read_full_budget_cached
from pyconsolida.cache_utils import flush_all_cache, get_folder_hash


def _time_function(func, **kwargs):
    """Run a function and return execution time in seconds."""
    start_time = time.time()
    func(**kwargs)
    return time.time() - start_time


@pytest.fixture
def test_args(temp_source_data, cache_folder, request):
    test_file = temp_source_data / "2023" / "12_Dicembre" / "1434" / "Analisi.xlsx"
    # Create unique cache folder for each test
    unique_cache = cache_folder / request.node.name
    unique_cache.mkdir(exist_ok=True)
    return {
        "filename": test_file,
        "folder_hash": get_folder_hash(test_file),
        "sum_fasi": False,
        "tipologie_skip": None,
        "cache": True,
        "cache_root": unique_cache,
    }


def test_cache_speedup(test_args):
    # First read and cached read
    end_time_first_read = _time_function(read_full_budget_cached, **test_args)
    end_time_cached = _time_function(read_full_budget_cached, **test_args)

    assert end_time_first_read > end_time_cached * 10


def test_cache_removal(test_args):
    # Initial read for reference
    _ = _time_function(read_full_budget_cached, **test_args)
    end_time_first_read = _time_function(read_full_budget_cached, **test_args)

    # Test with cache removed
    flush_all_cache(test_args["cache_root"])
    end_time_cache_removed = _time_function(read_full_budget_cached, **test_args)

    assert end_time_first_read < end_time_cache_removed * 10


def test_cache_disabled(test_args):
    # Initial read for reference
    end_time_first_read = _time_function(read_full_budget_cached, **test_args)

    # Test with cache disabled
    no_cache_args = test_args.copy()
    no_cache_args["cache"] = False
    end_time_cache_disabled = _time_function(read_full_budget_cached, **no_cache_args)

    assert end_time_first_read < end_time_cache_disabled * 10


def test_different_args(test_args):
    # Initial read for reference
    end_time_first_read = _time_function(read_full_budget_cached, **test_args)

    # Test with sum_fasi enabled
    sum_fasi_args = test_args.copy()
    sum_fasi_args["sum_fasi"] = True
    end_time_nosum = _time_function(read_full_budget_cached, **sum_fasi_args)
    end_time_nosum_second_read = _time_function(
        read_full_budget_cached, **sum_fasi_args
    )

    print(test_args["cache_root"], list(test_args["cache_root"].glob("*")))

    assert end_time_first_read < end_time_nosum * 10
    assert end_time_first_read > end_time_nosum_second_read * 10
