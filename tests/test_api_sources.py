"""Test for the /sources endpoint (document filenames for the source filter).

Points env.DATA_PATH at a temp dir so the result does not depend on the real ./data/ contents.
TestClient is built without `with`, so the app lifespan (warmup) does not fire.
"""

from fastapi.testclient import TestClient

from src.api import server


def test_sources_lists_supported_files(monkeypatch, tmp_path):
    for name in ("a.pdf", "b.md", "c.txt", "d.docx", "ignore.csv"):
        (tmp_path / name).write_text("x")
    monkeypatch.setattr(server.env, "DATA_PATH", str(tmp_path))

    client = TestClient(server.app)
    resp = client.get("/sources")

    assert resp.status_code == 200
    assert resp.json() == ["a.pdf", "b.md", "c.txt", "d.docx"]  # sorted, .csv excluded
