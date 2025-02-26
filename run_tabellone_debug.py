import tempfile
from pathlib import Path
from zipfile import ZipFile

from pyconsolida.main import process_tabellone


def run_tabellone_debug():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        test_data = Path(__file__).parent / "tests" / "assets" / "cantieri_test.zip"

        with ZipFile(test_data) as zip_file:
            zip_file.extractall(temp_dir)

        data_dir = temp_dir / "Cantieri_test"

        for _ in range(2):
            process_tabellone(
                directory=data_dir,
                progress_bar=True,
                debug_mode=True,
                cache=True,
            )


if __name__ == "__main__":
    dest_dir = run_tabellone_debug()
    print(f"Output saved to: {dest_dir}")
