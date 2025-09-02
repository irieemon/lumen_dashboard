import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from db import (
    init_db,
    upsert_initiative,
    get_initiatives,
    update_position,
    get_initiative,
)


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


def test_get_initiative_and_move(tmp_path, monkeypatch):
    _prepare_db(tmp_path, monkeypatch)
    new_id = upsert_initiative(None, "MoveMe", "", "yellow", "", 10, 10, "tester")
    update_position(new_id, 20, 30, "tester")
    row = get_initiative(new_id)
    assert row is not None
    assert row["x"] == 20
    assert row["y"] == 30
