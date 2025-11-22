from flask import jsonify, request
from backend.app import app
from backend.utils.dbUtils import fetch_all, fetch_one, _execute_insert, _execute_update, _execute_delete
from backend.utils.sanitize import sanitize_fields

def get_all_salas():
    return fetch_all(
        "SELECT nombre_sala, edificio, capacidad, tipo_sala FROM sala",
        ["nombre_sala", "edificio", "capacidad", "tipo_sala"]
    )

#Get all
@app.route("/api/salas", methods=["GET"])
def api_salas():
    return jsonify(get_all_salas()), 200

#Get one
@app.route("/api/salas/<path:edificio>/<nombre_sala>", methods=["GET"])
def api_sala_one(edificio, nombre_sala):
    r = fetch_one(
        "SELECT nombre_sala,edificio,capacidad,tipo_sala FROM sala WHERE edificio=%s AND nombre_sala=%s",
        (edificio, nombre_sala),
        ["nombre_sala","edificio","capacidad","tipo_sala"]
    )
    return (jsonify(r),200) if r else (jsonify({"error":"No encontrado"}),404)

#Create
@app.route("/api/salas", methods=["POST"])
def api_salas_create():
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["nombre_sala","edificio","tipo_sala"])
    required = ["nombre_sala","edificio","capacidad","tipo_sala"]
    if any(not data.get(f) for f in required):
        return jsonify({"error":"Campos obligatorios faltan"}), 400
    ok, err = _execute_insert(
        "INSERT INTO sala (nombre_sala,edificio,capacidad,tipo_sala) VALUES (%s,%s,%s,%s)",
        (data.get("nombre_sala"), data.get("edificio"),
         data.get("capacidad"), data.get("tipo_sala"))
    )
    if not ok:
        return jsonify({"error":err}), 400
    return jsonify({"message":"Sala creada"}), 201

# Update
@app.route("/api/salas/<path:edificio>/<nombre_sala>", methods=["PUT"])
def api_sala_update(edificio, nombre_sala):
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["capacidad","tipo_sala"])  # capacidad numérica se ignora si no string
    ok, err = _execute_update(
        "UPDATE sala SET capacidad=%s, tipo_sala=%s WHERE edificio=%s AND nombre_sala=%s",
        (data.get("capacidad"), data.get("tipo_sala"), edificio, nombre_sala)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

#Delete
@app.route("/api/salas/<path:edificio>/<nombre_sala>", methods=["DELETE"])
def api_sala_delete(edificio, nombre_sala):
    ok, err = _execute_delete("DELETE FROM sala WHERE edificio=%s AND nombre_sala=%s", (edificio, nombre_sala))
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)
