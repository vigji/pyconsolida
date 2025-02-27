from pathlib import Path

import pandas as pd


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
                and df[col].dropna().astype(str).str.startswith("{").all()
            ):
                df[col] = df[col].apply(lambda x: set(str(item) for item in x))

    # Remove hash columns from comparison
    hash_cols = [
        col for col in df1.columns if isinstance(col, str) and "hash" in col.lower()
    ]
    df1_filtered = df1.drop(columns=hash_cols, errors="ignore")
    df2_filtered = df2.drop(columns=hash_cols, errors="ignore")

    try:
        pd.testing.assert_frame_equal(
            df1_filtered.sort_index(axis=1),
            df2_filtered.sort_index(axis=1),
            check_dtype=False,
            check_index_type=False,
            check_column_type=False,
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

    supported_suffixes = {".xlsx", ".xls", ".pkl", ".pickle"}
    files1 = {
        get_base_name(f): f
        for f in dir1.iterdir()
        if f.is_file() and f.suffix.lower() in supported_suffixes
    }
    files2 = {
        get_base_name(f): f
        for f in dir2.iterdir()
        if f.is_file() and f.suffix.lower() in supported_suffixes
    }

    common_names = set(files1.keys()) & set(files2.keys())
    if not common_names:
        raise ValueError(f"No matching files found between {dir1} and {dir2}")

    for base_name in sorted(common_names):
        print(f"Comparing {files1[base_name]} and {files2[base_name]}")
        assert_dataframe_equal(files1[base_name], files2[base_name])
        print("good!")
        print("=================")


if __name__ == "__main__":
    assert_directory_exports_equal(
        # Path("/Users/vigji/Library/CloudStorage/OneDrive-I.co.p.Spa/Cantieri/exports/exported_250225-232627"),
        Path(
            "/Users/vigji/Library/CloudStorage/OneDrive-I.co.p.Spa/Cantieri/exports/exported_250226-080151"
        ),
        Path("/Users/vigji/Desktop/Cantieri/exports/exported_250227-002927"),
        # Path("/Users/vigji/Desktop/Cantieri/exports/exported_250227-085110"),
    )
