import logging
from pathlib import Path


def setup_logging(log_path: Path) -> None:
    """Configure logging with specified path for log file."""
    # Remove existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Setup new configuration
    logging.basicConfig(
        filename=log_path,
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )
