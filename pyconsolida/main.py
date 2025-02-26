import logging
import tempfile
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from pyconsolida.aggregations import load_loop_and_concat
from pyconsolida.delta import get_multiple_date_intervals, get_tabellone_delta
from pyconsolida.logging_config import setup_logging


def _process_tabellone_core(
    directory: Path,
    output_dir: Path | None = None,
    progress_bar: bool = True,
    cache: bool = True,
) -> Path:
    # timestamp for the folder name:
    tstamp = datetime.now().strftime("%y%m%d-%H%M%S")

    # Create destination directory
    if output_dir is None:
        dest_dir = directory / "exports" / f"exported_{tstamp}"
    else:
        dest_dir = output_dir / f"exported_{tstamp}"
    print(f"Output directory: {dest_dir}")
    dest_dir.mkdir(exist_ok=True, parents=True)

    setup_logging(dest_dir / f"log_{tstamp}.txt")
    logging.info(f"Lancio estrazione, export directory: {dest_dir}")

    # Load configuration files
    tipologie_fix = pd.read_excel(directory / "tipologie_fix.xlsx")
    tipologie_skip = pd.read_excel(directory / "tipologie_skip.xlsx")
    logging.info(f"File di correzione tipologie: {directory / 'tipologie_fix.xlsx'}")
    logging.info(f"File di tipologie da saltare: {directory / 'tipologie_fix.xlsx'}")

    # Find folders with latest formatting
    all_folders = list(directory.glob("202[1-9]/[0-1][0-9]_*/*"))
    all_folders += list(directory.glob("202[1-9]/*_[0-1][0-9]*/[0-9][0-9][0-9][0-9]*"))
    all_folders = sorted([f for f in all_folders if f.is_dir()])
    logging.info(f"Cartelle da analizzare trovate: {len(all_folders)}")

    # Main processing
    budget, reports = load_loop_and_concat(
        all_folders,
        tipologie_fix=tipologie_fix,
        tipologie_skip=tipologie_skip,
        progress_bar=progress_bar,
        report_filename=str(dest_dir / f"{tstamp}_report_fixed_tipologie.xlsx"),
        cache=cache,
    )

    # Save debug files
    budget.to_pickle(str(dest_dir / f"{tstamp}_tabellone.pickle"))
    reports.to_pickle(str(dest_dir / f"{tstamp}_reports.pickle"))

    # Generate delta for each interval
    for start, stop in get_multiple_date_intervals(True):
        interval_name = f"da{start.date()}-a-{stop.date()}"
        logging.info(f"Calcolo delta per intervallo {interval_name}")
        delta_df = get_tabellone_delta(budget, start, stop)
        delta_df.to_excel(
            str(dest_dir / f"{tstamp}_delta_tabellone_{interval_name}.xlsx")
        )

    if len(reports) > 0:
        reports.to_excel(str(dest_dir / f"{tstamp}_voci-costo_fix_report.xlsx"))

    tipologie_fix.to_excel(str(dest_dir / f"{tstamp}_tipologie-fix.xlsx"))

    return dest_dir


def process_tabellone(
    directory: Path | None = None,
    output_dir: Path | None = None,
    progress_bar: bool = True,
    debug_mode: bool = True,
    cache: bool = True,
) -> Path:
    """Process tabellone data and generate delta reports.

    Args:
        directory: Base directory containing the data
        output_dir: Optional output directory, defaults to directory/exports
        progress_bar: Whether to show progress bar
        debug_mode: Whether to run in debug mode
        cache: Whether to use caching

    Returns:
        Path to the destination directory
    """
    if debug_mode and directory is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            assets_folder = Path(__file__).parent.parent / "tests" / "assets"
            with ZipFile(assets_folder / "cantieri_test.zip") as zip_file:
                zip_file.extractall(temp_dir)
            # Run twice to test cache
            _process_tabellone_core(
                temp_dir / "Cantieri_test", output_dir, progress_bar, cache
            )
            _process_tabellone_core(
                temp_dir / "Cantieri_test", output_dir, progress_bar, cache
            )
    else:
        return _process_tabellone_core(directory, output_dir, progress_bar, cache)


if __name__ == "__main__":
    process_tabellone(debug_mode=True)
