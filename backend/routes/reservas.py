from flask import jsonify, request
from backend.app import app
from backend.utils.dbUtils import fetch_all, fetch_one, _execute_insert, _execute_update, _execute_delete
from backend.utils.sanitize import sanitize_fields

def get_all_reservas():
    print("[RESERVAS] Cargando reservas (con horas formateadas)")
    rows = fetch_all(
        """
        SELECT r.id_reserva,
               r.nombre_sala,
               r.edificio,
               r.fecha,
               TIME_FORMAT(t.hora_inicio,'%H:%i') AS hora_inicio,
               TIME_FORMAT(t.hora_fin,'%H:%i')   AS hora_fin,
               r.estado
        FROM reserva r
        JOIN turno t ON r.id_turno = t.id_turno
        ORDER BY r.id_reserva
        """,
        ["id_reserva","nombre_sala","edificio","fecha","hora_inicio","hora_fin","estado"]
    )
    print(f"[RESERVAS] Filas obtenidas: {len(rows)}")
    if rows:
        print(f"[RESERVAS] Ejemplo: {rows[0]}")
    return rows

#Get all
@app.route("/api/reservas", methods=["GET"])
def api_reservas():
    print("[REQ] /api/reservas")
    data = get_all_reservas()
    return jsonify(data), 200

#Get one
@app.route("/api/reservas/<int:id_reserva>", methods=["GET"])
def api_reserva_one(id_reserva):
    r = fetch_one(
        """
        SELECT r.id_reserva,r.nombre_sala,r.edificio,r.fecha,r.id_turno,
               TIME_FORMAT(t.hora_inicio,'%H:%i') AS hora_inicio,
               TIME_FORMAT(t.hora_fin,'%H:%i') AS hora_fin,r.estado
        FROM reserva r JOIN turno t ON r.id_turno=t.id_turno
        WHERE r.id_reserva=%s
        """,
        (id_reserva,),
        ["id_reserva","nombre_sala","edificio","fecha","id_turno","hora_inicio","hora_fin","estado"]
    )
    return (jsonify(r),200) if r else (jsonify({"error":"No encontrado"}),404)

#Create
@app.route("/api/reservas", methods=["POST"])
def api_reservas_create():
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["nombre_sala","edificio","fecha","estado"])
    required = ["id_reserva","nombre_sala","edificio","fecha","id_turno","estado"]
    if any(not data.get(f) for f in required):
        return jsonify({"error":"Campos obligatorios faltan"}), 400
    ok, err = _execute_insert(
        "INSERT INTO reserva (id_reserva,nombre_sala,edificio,fecha,id_turno,estado) VALUES (%s,%s,%s,%s,%s,%s)",
        (data.get("id_reserva"), data.get("nombre_sala"), data.get("edificio"),
         data.get("fecha"), data.get("id_turno"), data.get("estado"))
    )
    if not ok:
        return jsonify({"error":err}), 400
    return jsonify({"message":"Reserva creada"}), 201

# Update
@app.route("/api/reservas/<int:id_reserva>", methods=["PUT"])
def api_reserva_update(id_reserva):
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["nombre_sala","edificio","fecha","estado"])
    ok, err = _execute_update(
        "UPDATE reserva SET nombre_sala=%s, edificio=%s, fecha=%s, id_turno=%s, estado=%s WHERE id_reserva=%s",
        (data.get("nombre_sala"), data.get("edificio"), data.get("fecha"),
         data.get("id_turno"), data.get("estado"), id_reserva)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

#Delete
@app.route("/api/reservas/<int:id_reserva>", methods=["DELETE"])
def api_reserva_delete(id_reserva):
    ok, err = _execute_delete("DELETE FROM reserva WHERE id_reserva=%s", (id_reserva,))
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)
