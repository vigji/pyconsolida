from datetime import datetime
from unittest.mock import patch

import pytest

from pyconsolida.delta import get_multiple_date_intervals, input_data


def test_get_multiple_date_intervals_debug_mode():
    result = get_multiple_date_intervals(debug_mode=True)
    assert result == [(datetime(2023, 12, 1), datetime(2024, 2, 1))]


@patch("builtins.input")
def test_input_data(mock_input):
    mock_input.return_value = "12.2023"
    result = input_data("test")
    assert result == datetime(2023, 12, 1)
    mock_input.assert_called_once_with("Inserire mese test in formato MM.AAAA: ")


@patch("pyconsolida.delta.input_data")
@patch("builtins.input")
def test_get_multiple_date_intervals_single(mock_input, mock_input_data):
    # Setup mocks
    mock_input_data.side_effect = [
        datetime(2023, 1, 1),  # start date
        datetime(2023, 2, 1),  # end date
    ]
    mock_input.return_value = "n"  # don't add another interval

    result = get_multiple_date_intervals()
    assert result == [(datetime(2023, 1, 1), datetime(2023, 2, 1))]


@patch("pyconsolida.delta.input_data")
@patch("builtins.input")
def test_get_multiple_date_intervals_multiple(mock_input, mock_input_data):
    # Setup mocks
    mock_input_data.side_effect = [
        datetime(2023, 1, 1),  # first start
        datetime(2023, 2, 1),  # first end
        datetime(2023, 3, 1),  # second start
        datetime(2023, 4, 1),  # second end
    ]
    mock_input.side_effect = ["s", "n"]  # yes for first loop, no for second

    result = get_multiple_date_intervals()
    assert result == [
        (datetime(2023, 1, 1), datetime(2023, 2, 1)),
        (datetime(2023, 3, 1), datetime(2023, 4, 1)),
    ]


@patch("pyconsolida.delta.input_data")
def test_get_multiple_date_intervals_invalid_dates(mock_input_data):
    # Test start date after end date
    mock_input_data.side_effect = [
        datetime(2023, 2, 1),  # start after end
        datetime(2023, 1, 1),
    ]
    with pytest.raises(ValueError, match="La data di inizio deve essere precedente"):
        get_multiple_date_intervals()

    # Test date before 2021
    mock_input_data.side_effect = [
        datetime(2020, 1, 1),  # start before 2021
        datetime(2023, 1, 1),
    ]
    with pytest.raises(ValueError, match="La data di inizio deve essere compresa"):
        get_multiple_date_intervals()


@patch("builtins.input")
def test_input_data_invalid_format(mock_input):
    mock_input.return_value = "invalid"
    with pytest.raises(ValueError):
        input_data("test")
