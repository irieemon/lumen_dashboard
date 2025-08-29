import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from db import init_db, upsert_initiative, get_initiatives


def _prepare_db(tmp_path, monkeypatch):
    db_path = tmp_path / "valeff.db"
    monkeypatch.setenv("LUMEN_DB", str(db_path))
    init_db()


def test_value_effort_high(tmp_path, monkeypatch):
    _prepare_db(tmp_path, monkeypatch)
    new_id = upsert_initiative(None, "ValEffHigh", "", "red", "", 80, 90, "tester")
    df = get_initiatives()
    row = df[df["id"] == new_id].iloc[0]
    assert row["value"] == "High"
    assert row["effort"] == "High"


def test_value_effort_low_medium(tmp_path, monkeypatch):
    _prepare_db(tmp_path, monkeypatch)
    new_id = upsert_initiative(None, "ValEffLowMed", "", "red", "", 50, 10, "tester")
    df = get_initiatives()
    row = df[df["id"] == new_id].iloc[0]
    assert row["value"] == "Low"
    assert row["effort"] == "Medium"
