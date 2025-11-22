from flask import jsonify, request
from backend.app import app
from backend.utils.dbUtils import fetch_all, fetch_one, _execute_insert, _execute_update, _execute_delete
from backend.utils.sanitize import sanitize_fields

def get_all_participantes():
    return fetch_all(
        "SELECT ci, nombre, apellido, fecha_nac, genero FROM participante",
        ["ci", "nombre", "apellido", "fecha_nac", "genero"]
    )

#Get all
@app.route("/api/participantes", methods=["GET"])
def api_participantes():
    return jsonify(get_all_participantes()), 200

#Get one
@app.route("/api/participantes/<ci>", methods=["GET"])
def api_participante_one(ci):
    r = fetch_one(
        "SELECT ci,nombre,apellido,fecha_nac,genero FROM participante WHERE ci=%s",
        (ci,),
        ["ci","nombre","apellido","fecha_nac","genero"]
    )
    return (jsonify(r), 200) if r else (jsonify({"error":"No encontrado"}),404)

# Update
@app.route("/api/participantes/<ci>", methods=["PUT"])
def api_participante_update(ci):
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["nombre","apellido","genero","fecha_nac"])
    ok, err = _execute_update(
        "UPDATE participante SET nombre=%s, apellido=%s, fecha_nac=%s, genero=%s WHERE ci=%s",
        (data.get("nombre"), data.get("apellido"), data.get("fecha_nac"), data.get("genero"), ci)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

#Create
@app.route("/api/participantes", methods=["POST"])
def api_participantes_create():
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["ci","nombre","apellido","genero","fecha_nac"])
    required = ["ci","nombre","apellido"]
    if any(not data.get(f) for f in required):
        return jsonify({"error":"Campos obligatorios faltan"}), 400
    ok, err = _execute_insert(
        "INSERT INTO participante (ci,nombre,apellido,fecha_nac,genero) VALUES (%s,%s,%s,%s,%s)",
        (data.get("ci"), data.get("nombre"), data.get("apellido"),
         data.get("fecha_nac") or None, data.get("genero") or None)
    )
    if not ok:
        return jsonify({"error":err}), 400
    return jsonify({"message":"Participante creado"}), 201

#Delete
@app.route("/api/participantes/<ci>", methods=["DELETE"])
def api_participante_delete(ci):
    ok, err = _execute_delete("DELETE FROM participante WHERE ci=%s", (ci,))
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)


