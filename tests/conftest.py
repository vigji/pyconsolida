from pathlib import Path

import pytest


@pytest.fixture
def assets_folder():
    return Path(__file__).parent / "assets"
