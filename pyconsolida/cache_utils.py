import hashlib
from functools import lru_cache
from pathlib import Path

import git


def _remove_cache_folder(folder: Path):
    for item in folder.glob("**/*"):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            item.rmdir()
    folder.rmdir()


def flush_cache_subfolder(folder: Path):
    folder = Path(folder)
    cache_folder = folder / "cached"
    _remove_cache_folder(cache_folder)


def flush_all_cache(folder: Path):
    """Remove all cached data folders and their contents."""
    folder = Path(folder)

    # Find all cache folders matching the pattern /*/*/*/cached
    cache_folders = folder.glob("*/*/*/cached")
    for cache_folder in cache_folders:
        _remove_cache_folder(cache_folder)


@lru_cache(maxsize=1)
def get_repo_version():
    N_HASH_CHARS = 6

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    return sha[:N_HASH_CHARS]


@lru_cache(maxsize=1)
def get_folder_hash(folder_path):
    """Compute SHA-256 hash of all files in a folder using pathlib."""
    N_HASH_CHARS = 10
    sha256_hash = hashlib.sha256()
    # Create a Path object for the folder
    folder = Path(folder_path)
    # Iterate over all files in the folder, including subfolders
    for file_path in sorted(folder.rglob("*")):
        # escludo cache e empty folders:
        if file_path.is_file() and file_path.parent.name != "cached":
            # Hash each file
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()[:N_HASH_CHARS]


def get_args_hash(**kwargs):
    """Compute SHA-256 hash of all arguments."""
    N_HASH_CHARS = 10
    sha256_hash = hashlib.sha256()
    for key, value in kwargs.items():
        sha256_hash.update(f"{key}:{value}".encode("utf-8"))
    return sha256_hash.hexdigest()[:N_HASH_CHARS]


if __name__ == "__main__":
    import time

    from pyconsolida.budget_reader import read_full_budget_cached

    data_loc = Path("/Users/vigji/Desktop/Cantieri_test")
    test_file = data_loc / "2023" / "12_Dicembre" / "1434" / "Analisi.xlsx"

    args = {
        "filename": test_file,
        "folder_hash": get_folder_hash(test_file),
        "sum_fasi": False,
        "tipologie_skip": None,
        "cache": True,
    }

    def _time_function(func, **kwargs):
        """Run a function and return execution time in seconds."""
        start_time = time.time()
        func(**kwargs)
        return time.time() - start_time

    end_time_first_read = _time_function(read_full_budget_cached, **args)
    end_time_cached = _time_function(read_full_budget_cached, **args)

    flush_cache_subfolder(test_file.parent)
    end_time_cache_removed = _time_function(read_full_budget_cached, **args)

    new_args = args.copy()
    new_args["cache"] = False
    end_time_cache_disabled = _time_function(read_full_budget_cached, **new_args)

    new_args_nosum = args.copy()
    new_args_nosum["sum_fasi"] = True
    end_time_nosum = _time_function(read_full_budget_cached, **new_args_nosum)

    end_time_nosum_second_read = _time_function(
        read_full_budget_cached, **new_args_nosum
    )

    baseline = end_time_first_read
    expected_factor = 10
    assert baseline > end_time_cached * expected_factor
    assert baseline < end_time_cache_removed * expected_factor
    assert baseline < end_time_cache_disabled * expected_factor
    assert baseline < end_time_nosum * expected_factor
    assert baseline > end_time_nosum_second_read * expected_factor

    # flush_cache_subfolder(test_file.parent)
