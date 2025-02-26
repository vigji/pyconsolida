from pathlib import Path


def flush_cache(folder: Path):
    """Remove all cached data folders and their contents."""
    folder = Path(folder)

    # Find all cache folders matching the pattern /*/*/*/cached
    cache_folders = folder.glob("*/*/*/cached")

    # Remove each cache folder and its contents
    for folder in cache_folders:
        if folder.is_dir():
            for item in folder.glob("**/*"):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            folder.rmdir()


if __name__ == "__main__":
    flush_cache(Path("/Users/vigji/Desktop/Cantieri_test"))
