import pandas as pd
from pathlib import Path

def test_something(temp_source_data):
    # temp_source_data is the Path to the extracted files
    assert (temp_source_data / "cantieri_test").exists()

def assert_dataframe_equal(file1_path: Path, file2_path: Path) -> None:
    """Compare two files (Excel or pickle) for identical content using pandas."""
    def read_file(path: Path) -> pd.DataFrame:
        suffix = path.suffix.lower()
        if suffix in [".xlsx", ".xls"]:
            return pd.read_excel(path)
        elif suffix in [".pickle", ".pkl"]:
            return pd.read_pickle(path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    df1 = read_file(file1_path)
    df2 = read_file(file2_path)

    # Convert string-represented sets back to actual sets for comparison
    for df in [df1, df2]:
        for col in df.columns:
            if (
                df[col].dtype == "object"
                and df[col].head().astype(str).str.startswith("{").all()
            ):
                df[col] = df[col].apply(lambda x: set(eval(x)) if isinstance(x, str) else x)

    try:
        pd.testing.assert_frame_equal(
            df1,
            df2,
            check_dtype=False,  # Skip dtype checking as Excel may import numbers differently
            check_index_type=False,  # Skip index type checking
            check_column_type=False,  # Skip column type checking
        )
    except AssertionError as e:
        print(f"Assertion failed for {file1_path} and {file2_path}")
        raise e

def assert_directory_exports_equal(dir1: Path, dir2: Path) -> None:
    """Compare all matching files (by name without timestamp) in two directories."""

    dir1 = Path(dir1)
    dir2 = Path(dir2)
    
    def get_base_name(path: Path) -> str:
        """Get filename without timestamp prefix (removes YYMMDD-HHMMSS_)."""
        name = path.name
        if not (len(name) > 13 and name[6] == "-" and name[13] == "_"):
            raise ValueError(
                f"File {path} does not follow the expected format: "
                "YYMMDD-HHMMSS_filename.extension"
            )
        return name[14:]
    
    # Get all Excel and pickle files from both directories
    supported_suffixes = {".xlsx", ".xls", ".pkl", ".pickle"}
    files1 = {get_base_name(f): f for f in dir1.iterdir() 
              if f.is_file() and f.suffix.lower() in supported_suffixes}
    files2 = {get_base_name(f): f for f in dir2.iterdir() 
              if f.is_file() and f.suffix.lower() in supported_suffixes}
    
    # Find common base names
    common_names = set(files1.keys()) & set(files2.keys())
    if not common_names:
        raise ValueError(f"No matching files found between {dir1} and {dir2}")
    
    # Compare each pair of files
    for base_name in sorted(common_names):
        assert_dataframe_equal(files1[base_name], files2[base_name])

assert_directory_exports_equal(
   "/Users/vigji/Desktop/Cantieri_test/exports/expected_export",
   "/Users/vigji/Desktop/Cantieri_test/exports/exported_250226-104858"
)