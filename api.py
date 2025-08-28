from flask import Flask, request, jsonify
from flask_cors import CORS
from db import (
    init_db,
    get_initiatives,
    update_position,
    upsert_initiative,
    delete_initiative,
    get_last_updated,
)

init_db()

app = Flask(__name__)
CORS(app)


@app.get("/api/initiatives")
def api_get_initiatives():
    df = get_initiatives()
    return jsonify({"initiatives": df.to_dict(orient="records"), "last_updated": get_last_updated()})


@app.post("/api/positions")
def api_save_positions():
    data = request.get_json(force=True)
    user = data.get("user", "user")
    for pos in data.get("positions", []):
        update_position(pos["id"], pos["x"], pos["y"], user)
    return jsonify({"status": "ok", "last_updated": get_last_updated()})


@app.post("/api/initiative")
def api_upsert_initiative():
    data = request.get_json(force=True)
    new_id = upsert_initiative(
        data.get("id"),
        data.get("title"),
        data.get("details", ""),
        data.get("color", "pink"),
        data.get("category", ""),
        data.get("x", 50),
        data.get("y", 50),
        data.get("user", "user"),
    )
    return jsonify({"id": new_id, "last_updated": get_last_updated()})


@app.delete("/api/initiative/<int:initiative_id>")
def api_delete_initiative(initiative_id: int):
    delete_initiative(initiative_id)
    return jsonify({"status": "ok", "last_updated": get_last_updated()})


@app.get("/api/last_updated")
def api_last_updated():
    return jsonify({"last_updated": get_last_updated()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
