def test_insert_unique_and_duplicate(sqlite_manager):
    db = sqlite_manager
    db.sanity_check()

    tbl = db.ensure_table("Acme Corp")
    assert tbl == "vt_feb27a647c4fec6d2b6890c2ffe75196"

    # First insert should succeed …
    assert db.insert(tbl, "example.com", "domain") is True

    # Second identical insert is ignored.
    assert db.insert(tbl, "example.com", "domain") is False

    # Verify there is exactly one row
    cnt = db._conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    assert cnt == 1