import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from db import init_db, add_initiative, get_initiatives


def test_add_and_retrieve(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setenv("LUMEN_DB", str(test_db))
    init_db()
    add_initiative("Test", "Details", "blue", "Cat", 10, 20, "tester")
    df = get_initiatives()
    assert "Test" in df["title"].values
