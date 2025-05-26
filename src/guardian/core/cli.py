from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="guardian",
        description=(
            "Guardian - turn a single JSON rule file into a full VirusTotal "
            "threat-hunting run. For each entity/query pair it streams results, "
            "deduplicates them, writes the delta to SQLite and (optionally) fires "
            "off a notification."
        ),
        epilog=(
            "Example:\n"
            "  guardian --json-entities rules.json --notify --verbose\n"
            "\n"
            "Need help?  https://github.com/hexastrike/guardian"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument(
        "--json-entities",
        required=True,
        metavar="FILE",
        help="Path to your entities.json rule file.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Chatty output: include DEBUG-level log lines.",
    )
    p.add_argument(
        "--notify",
        action="store_true",
        help="Fire a notification for every brand-new VirusTotal hit.",
    )

    return p.parse_args()
