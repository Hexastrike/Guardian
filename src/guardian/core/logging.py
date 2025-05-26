from __future__ import annotations

import logging

from datetime import datetime
from pathlib import Path


class LogManager:
    """Configure project-wide logging once."""

    def __init__(self, *, verbose: bool, log_dir: Path) -> None:
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"hx_guardian_{datetime.utcnow():%Y_%m}.log"

        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG if verbose else logging.INFO,
            format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
        )
        logging.getLogger(__name__).debug("Log file: %s", log_file)
        