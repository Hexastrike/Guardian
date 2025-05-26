from __future__ import annotations

import logging
import json

from typing import Any, Iterable, List
from pathlib import Path

from guardian.db.sqlite import SQLiteManager
from guardian.integrations.virustotal import VirusTotalClient
from guardian.runtime.notifications import Notifier


class QueryApp:

    def __init__(self, db_manager: SQLiteManager, vt_cli: VirusTotalClient, notifier: Notifier | None = None,) -> None:
        self._store = db_manager
        self._vtcli = vt_cli
        self._notifier = notifier

    def run(self, entities_file: Path) -> None:
        """High-level driver."""
        entities = self._load_entities(entities_file)
        if not entities:
            logging.warning("No entities found - nothing to do.")
            return

        for entity in entities:
            self._process_entity(entity)

        logging.info('Finished processing entities, amount=%d', len(entities))

    # Internal helpers
    def _load_entities(self, path: Path) -> List[dict[str, Any]]:
        """Return the list of provided entities or an empty list on error."""
        self._store.sanity_check()
        try:
            with path.open("r", encoding="utf-8") as fp:
                return json.load(fp).get("entities", [])
        except Exception as exc:
            logging.error('Reading entities failed, file="%s", error="%s"', path, exc)
            return []

    def _process_entity(self, entity: dict[str, Any]) -> None:
        name: str = entity.get("name", "").strip()
        logging.info('Processing entity, entity="%s"', name)

        if not name:
            logging.warning("Skip entity without name field")
            return

        table = self._store.ensure_table(name)
        queries: Iterable[dict[str, Any]] = entity.get("queries", [])

        if not queries:
            logging.info('No queries detected, entity="%s"', name)
            return

        for q in queries:
            self._run_query(name, table, q)

    def _run_query(self, entity: str, table: str, qdef: dict[str, Any]) -> None:
        label = (qdef.get("label") or "unlabeled_query").strip()
        query = qdef.get("query", [])

        if not query:
            logging.debug('Empty query detected, entity="%s" label="%s"', entity, label)
            return

        logging.info('Processing query, entity="%s" label="%s"', entity, label)

        found_new = False
        for result in self._vtcli.search(query):

            if result.id and self._store.insert(table, result.id, result.type):
                found_new = True
                logging.info('New query hit, entity="%s" label="%s" resource_id="%s"', entity, label, result.id)

                # Send notification if notifier is present
                if self._notifier:
                    self._notifier.notify(
                        {
                            "entity": entity,
                            "label": label,
                            "resource_id": result.id,
                            "resource_type": result.type,
                        }
                    )

        if not found_new:
            logging.info('No new query hits, entity="%s" label="%s"', entity, label)
