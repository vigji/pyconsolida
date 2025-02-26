from pyconsolida.main import process_tabellone
from pyconsolida.utils.comparison import assert_directory_exports_equal


def test_something(temp_source_data):
    # temp_source_data is the Path to the extracted files
    assert (temp_source_data).exists()


def test_main(temp_source_data, expected_exports_folder):
    # Run main process
    dest_dir = process_tabellone(
        directory=temp_source_data,
        output_dir=None,
        progress_bar=True,
        debug_mode=True,
    )

    assert_directory_exports_equal(dest_dir, expected_exports_folder)


if __name__ == "__main__":
    assert_directory_exports_equal(
        "/Users/vigji/Desktop/Cantieri_test/exports/expected_export",
        "/Users/vigji/Desktop/Cantieri_test/exports/exported_250226-105856",
    )
