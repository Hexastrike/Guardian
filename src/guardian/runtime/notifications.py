from __future__ import annotations

import logging

from typing import Any

class Notifier:
    """
    Bare-bones alerting stub.

    Replace / extend notify() to point at Slack, Teams, SMTP, etc.
    """
    def __init__(self, channel: str = "stdout") -> None:
        self._channel = channel.lower()

    # Helpers
    def _send_stdout(self, message: str) -> None:
        print(message, flush=True)

    # Public API
    def notify(self, data: dict[str, Any]) -> None:
        """
        Send a single alert.

        data comes from QueryApp and contains at least:
           entity, label, resource_id, resource_type
        """
        msg = (
            "[Guardian] "
            f"entity='{data['entity']}' "
            f"label='{data['label']}' "
            f"resource_id='{data['resource_id']}' "
            f"resource_type='{data['resource_type']}'"
        )

        if self._channel == "stdout":
            self._send_stdout(msg)
        else:
            logging.warning("Notification channel '%s' not implemented", self._channel)
