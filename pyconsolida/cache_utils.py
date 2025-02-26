import hashlib
from functools import lru_cache
from pathlib import Path

import git

from pyconsolida.sheet_specs import CACHE_PATH, DATA_PATH


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


def flush_all_cache(folder: Path = CACHE_PATH):
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


def get_cache_directory(
    target_subdir: str,
    data_path: Path = DATA_PATH,
    cache_root: Path = CACHE_PATH,
    create_if_missing: bool = True,
):
    """Ensure the corresponding cache directory exists."""
    data_path = Path(data_path).resolve()
    target_subdir = Path(target_subdir).resolve()

    if not target_subdir.is_relative_to(data_path):
        print(
            f"Target subdirectory {target_subdir} is not inside data_path {data_path}"
        )
        raise ValueError("Target subdirectory is not inside data_path")

    relative_subdir = target_subdir.relative_to(data_path)
    cache_dir = Path(cache_root) / relative_subdir / "cached"
    if create_if_missing:
        cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


if __name__ == "__main__":
    # Example usage
    data_path = "/Users/vigji/Desktop/Cantieri_test"
    cache_root = "/Users/vigji/Desktop/cache_location"
    target_subdir = "/Users/vigji/Desktop/Cantieri_test/2024/12_December/1435"

    cache_dir = get_cache_directory(target_subdir)
    print(f"Cache directory created at: {cache_dir}")
