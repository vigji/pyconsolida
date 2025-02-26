"""This script extract all data used during one year of activity.

The input folder (specified as DIRECTORY) has to be organized in the following way:
"""
from pyconsolida.main import process_tabellone
from pathlib import Path

if __name__ == "__main__":
    # Configuration
    DIRECTORY = (
        Path("/Users/vigji/Desktop/Cantieri_test")
        if Path("/Users/vigji").exists()
        else Path("/myshare/cantieri")
    )
    PROGRESS_BAR = True
    OUTPUT_DIR = None  # Path("/Users/vigji/Desktop/exports")
    DEBUG_MODE = True

    # Run main process
    budget, reports = process_tabellone(
        directory=DIRECTORY,
        output_dir=OUTPUT_DIR,
        progress_bar=PROGRESS_BAR,
        debug_mode=DEBUG_MODE,
    )
