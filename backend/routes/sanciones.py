from flask import jsonify, request
from backend.app import app
from backend.utils.dbUtils import fetch_all, fetch_one, _execute_insert, _execute_update, _execute_delete
from backend.utils.sanitize import sanitize_fields

def get_all_sanciones():
    return fetch_all(
        "SELECT participante_ci, fecha_inicio, fecha_fin FROM sancion_cuenta",
        ["participante_ci", "fecha_inicio", "fecha_fin"]
    )

#Get all
@app.route("/api/sanciones", methods=["GET"])
def api_sanciones():
    return jsonify(get_all_sanciones()), 200

#Get one
@app.route("/api/sanciones/<participante_ci>/<fecha_inicio>/<fecha_fin>", methods=["GET"])
def api_sancion_one(participante_ci, fecha_inicio, fecha_fin):
    r = fetch_one(
        "SELECT participante_ci,fecha_inicio,fecha_fin FROM sancion_cuenta WHERE participante_ci=%s AND fecha_inicio=%s AND fecha_fin=%s",
        (participante_ci, fecha_inicio, fecha_fin),
        ["participante_ci","fecha_inicio","fecha_fin"]
    )
    return (jsonify(r),200) if r else (jsonify({"error":"No encontrado"}),404)

#Create
@app.route("/api/sanciones", methods=["POST"])
def api_sanciones_create():
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["participante_ci","fecha_inicio","fecha_fin"])
    required = ["participante_ci","fecha_inicio","fecha_fin"]
    if any(not data.get(f) for f in required):
        return jsonify({"error":"Campos obligatorios faltan"}), 400
    ok, err = _execute_insert(
        "INSERT INTO sancion_cuenta (participante_ci,fecha_inicio,fecha_fin) VALUES (%s,%s,%s)",
        (data.get("participante_ci"), data.get("fecha_inicio"), data.get("fecha_fin"))
    )
    if not ok:
        return jsonify({"error":err}), 400
    return jsonify({"message":"Sanción creada"}), 201

# Update
@app.route("/api/sanciones/<participante_ci>/<fecha_inicio>/<fecha_fin>", methods=["PUT"])
def api_sancion_update(participante_ci, fecha_inicio, fecha_fin):
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["fecha_inicio_new","fecha_fin_new"])
    ok, err = _execute_update(
        "UPDATE sancion_cuenta SET fecha_inicio=%s, fecha_fin=%s WHERE participante_ci=%s AND fecha_inicio=%s AND fecha_fin=%s",
        (data.get("fecha_inicio_new") or fecha_inicio,
         data.get("fecha_fin_new") or fecha_fin,
         participante_ci, fecha_inicio, fecha_fin)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

#Delete
@app.route("/api/sanciones/<participante_ci>/<fecha_inicio>/<fecha_fin>", methods=["DELETE"])
def api_sancion_delete(participante_ci, fecha_inicio, fecha_fin):
    ok, err = _execute_delete(
        "DELETE FROM sancion_cuenta WHERE participante_ci=%s AND fecha_inicio=%s AND fecha_fin=%s",
        (participante_ci, fecha_inicio, fecha_fin)
    )
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)
