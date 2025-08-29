import sys
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from flask.testing import FlaskClient


def _get_client(tmp_path, monkeypatch) -> FlaskClient:
    """Return a Flask test client backed by a temporary database."""
    db_path = tmp_path / "api_test.db"
    monkeypatch.setenv("LUMEN_DB", str(db_path))
    import api
    importlib.reload(api)
    return api.app.test_client()


def test_api_upsert_and_fetch(tmp_path, monkeypatch):
    client = _get_client(tmp_path, monkeypatch)
    payload = {
        "title": "API Test",
        "details": "details",
        "color": "blue",
        "category": "Cat",
        "x": 10,
        "y": 20,
        "user": "tester",
    }
    res = client.post("/api/initiative", json=payload)
    assert res.status_code == 200
    new_id = res.get_json()["id"]
    assert isinstance(new_id, int)

    res = client.get("/api/initiatives")
    data = res.get_json()["initiatives"]
    titles = [i["title"] for i in data]
    assert payload["title"] in titles
