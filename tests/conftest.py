from pathlib import Path
from zipfile import ZipFile

import pytest


@pytest.fixture
def assets_folder():
    return Path(__file__).parent / "assets"


@pytest.fixture
def temp_source_data(tmp_path, assets_folder):
    zip_path = assets_folder / "cantieri_test.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Test data zip file not found: {zip_path}")

    with ZipFile(zip_path) as zip_file:
        zip_file.extractall(tmp_path)

    # Check that the data was extracted successfully
    data_folder = tmp_path / "cantieri_test"
    if not data_folder.exists() or not data_folder.is_dir():
        raise RuntimeError(f"Failed to extract data folder to {data_folder}")

    return tmp_path
