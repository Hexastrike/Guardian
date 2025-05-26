from __future__ import annotations

import logging
import vt

from typing import (
    Any,
    Iterable, 
    Optional
)

class VirusTotalClient:
    """Context-managed VirusTotal Client with a simple search helper."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client: Optional[vt.Client] = None

    def __enter__(self) -> "VirusTotalClient":
        self._client = vt.Client(self._api_key)
        return self

    def __exit__(self, *_exc) -> None:
        self._client and self._client.close()

    def search(self, query: str, limit: int = 50) -> Iterable[dict[str, Any]]:
        if not self._client:
            raise RuntimeError("VT client not initialised")

        logging.debug('VirusTotal Query, query="%s"', query)

        try :
            return self._client.iterator("/intelligence/search", params={"query": query}, limit=limit)
        except Exception as exc:
            logging.error("Error searching VirusTotal with query %s: %s", query, exc)
            return iter([])
