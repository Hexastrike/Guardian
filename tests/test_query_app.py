import json

from pathlib import Path

from guardian.runtime.query import QueryApp


class _DummyResult:  # mimics minimal vt API result object
    def __init__(self, rid: str, rtype: str) -> None:
        self.id = rid
        self.type = rtype


class DummyVirusTotalClient:
    """Pretends to be VirusTotal without network calls."""

    def search(self, _query):
        # Always return 2 fresh hits so we can assert they’re inserted.
        return [_DummyResult("bar.com", "domain"), _DummyResult("foo.com", "domain")]


def test_query_app_persists_hits(tmp_path: Path, sqlite_manager):
    entities_payload = {
        "entities": [
            {
                "name": "Acme",
                "queries": [
                    {
                        "label": "Acme search",
                        "query": "entity:domain main_icon_dhash:acme NOT parent_domain:acme.com"
                    }
                ],
            }
        ]
    }
    entities_json = tmp_path / "entities.json"
    entities_json.write_text(json.dumps(entities_payload), encoding="utf-8")

    db = sqlite_manager
    db.sanity_check()

    vt = DummyVirusTotalClient()

    QueryApp(db, vt).run(entities_json)

    tbl = db.ensure_table("Acme")
    count = db._conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]  # noqa: SLF001
    assert count == 2