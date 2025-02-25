from pathlib import Path
from zipfile import ZipFile

import pytest


@pytest.fixture
def assets_folder():
    return Path(__file__).parent / "assets"


@pytest.fixture
def temp_source_data(tmp_path, assets_folder):
    zip_path = assets_folder / "cantieri_test.zip"
    with ZipFile(zip_path) as zip_file:
        zip_file.extractall(tmp_path)
    return tmp_path
