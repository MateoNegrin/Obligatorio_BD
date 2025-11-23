from flask import request, jsonify
from backend.app import app
from backend.utils.dbUtils import fetch_one
from backend.utils.sanitize import sanitize_input

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    correo = sanitize_input(data.get("correo", ""))
    password = sanitize_input(data.get("password", ""))
    if not correo or not password:
        return jsonify({"error": "Faltan credenciales"}), 400
    row = fetch_one(
        "SELECT correo FROM login WHERE correo=%s AND password=%s",
        (correo, password),
        ["correo"]
    )
    if not row:
        return jsonify({"error": "Credenciales inválidas"}), 401
    return jsonify({"correo": row["correo"]}), 200
