#!/usr/bin/env python3

from __future__ import annotations

import logging
import os

from contextlib import ExitStack
from dotenv import find_dotenv, load_dotenv
from pathlib import Path
from typing import Final

import guardian.core.cli
import guardian.core.logging
import guardian.db.sqlite
import guardian.integrations.virustotal
import guardian.runtime.query
import guardian.runtime.notifications


# Constants
PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parent
DB_FILE: Final[Path] = PACKAGE_ROOT / "guardian.sqlite3"
LOG_DIR: Final[Path] = PACKAGE_ROOT / "logs"

# Helpers
def _load_env() -> None:
    """
    Populate os.environ from the closest .env file, if any.
    Raises on failure so we exit fast in CI / prod.
    """
    env_path = find_dotenv(usecwd=True) # walks up until it finds a .env
    if env_path:
        load_dotenv(env_path, override=False)
    else:
        logging.debug("No .env file discovered — relying on real env.")

def _get_vt_api_key() -> str:
    vt_api_key = os.getenv("VT_API_KEY", "").strip()
    if not vt_api_key:
        raise SystemExit("Environment variable VT_API_KEY is missing.")
    return vt_api_key

# Main
def main() -> None:
    args = guardian.core.cli.parse_args()

    # Logging
    guardian.core.logging.LogManager(verbose=args.verbose, log_dir=LOG_DIR)

    # Environment
    _load_env()
    vt_api_key = _get_vt_api_key()

    # Dependency construction & lifetime management
    # Manage both the VirusTotal client and any future context-managed dependencies in one place
    with ExitStack() as stack:
        # Keep one sqlite connection for the whole run
        db = guardian.db.sqlite.SQLiteManager(DB_FILE)

        vt_cli = stack.enter_context(guardian.integrations.virustotal.VirusTotalClient(vt_api_key))

        notifier = guardian.runtime.notifications.Notifier() if args.notify else None

        # Run application
        guardian.runtime.query.QueryApp(db, vt_cli, notifier).run(Path(args.json_entities))

    logging.info("Bye Master...")

# Entrypoint
if __name__ == "__main__":
    main()
