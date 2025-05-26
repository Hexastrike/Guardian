from __future__ import annotations

import sys
import logging

from datetime import datetime
from pathlib import Path


class LogManager:
    """
    Configure project-wide logging exactly once.

    Logs go to stdout and to a month-rotated file in log_dir/.
    Respects the verbose flag for DEBUG vs. INFO level.
    Safe to instantiate multiple times - only the first call adds handlers.
    """

    _configured = False # class-level guard

    def __init__(self, *, verbose: bool, log_dir: Path) -> None:
        if LogManager._configured: # already done: no-op
            return

        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"hx_guardian_{datetime.utcnow():%Y_%m}.log"

        level = logging.DEBUG if verbose else logging.INFO
        fmt   = "%(asctime)s %(levelname)s %(name)s %(message)s"
        formatter = logging.Formatter(fmt)

        root = logging.getLogger()
        root.setLevel(level)

        # File handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root.addHandler(file_handler)

        # Stdout handler
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        root.addHandler(stream_handler)

        root.debug("Log file initialised → %s", log_file)
        LogManager._configured = True
        