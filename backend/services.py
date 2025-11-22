from mysql.connector import Error
from config import get_connection
from flask import Flask, jsonify, request
from flask_cors import CORS  

def _to_json_safe(v):
    # normaliza date/time a string ISO
    try:
        import datetime
        if isinstance(v, (datetime.date, datetime.time, datetime.datetime)):
            return v.isoformat()
    except Exception:
        pass
    return v

def fetch_all(query, cols):
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [ { cols[i]: _to_json_safe(row[i]) for i in range(len(cols)) } for row in rows ]
    except Error as e:
        print(f"[DB] Error en fetch_all: {e}")
        return []

def fetch_one(query, params, cols):
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return None
        return { cols[i]: _to_json_safe(row[i]) for i in range(len(cols)) }
    except Error as e:
        print(f"[DB] Error en fetch_one: {e}")
        return None

def get_all_participantes():
    return fetch_all(
        "SELECT ci, nombre, apellido, fecha_nac, genero FROM participante",
        ["ci", "nombre", "apellido", "fecha_nac", "genero"]
    )

def get_all_salas():
    return fetch_all(
        "SELECT nombre_sala, edificio, capacidad, tipo_sala FROM sala",
        ["nombre_sala", "edificio", "capacidad", "tipo_sala"]
    )

def get_all_sanciones():
    return fetch_all(
        "SELECT participante_ci, fecha_inicio, fecha_fin FROM sancion_cuenta",
        ["participante_ci", "fecha_inicio", "fecha_fin"]
    )

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

def _execute_insert(query, params):
    conn = get_connection()
    if not conn:
        return False, "Sin conexión a la base de datos"
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except Error as e:
        return False, str(e)

def _execute_update(query, params):
    conn = get_connection()
    if not conn: return False, "Sin conexión"
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        affected = cur.rowcount
        cur.close(); conn.close()
        return affected > 0, None
    except Error as e:
        return False, str(e)

def _execute_delete(query, params):
    conn = get_connection()
    if not conn: return False, "Sin conexión"
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        affected = cur.rowcount
        cur.close(); conn.close()
        return affected > 0, None
    except Error as e:
        return False, str(e)

# Endpoints
app = Flask(__name__)
CORS(app)  

@app.route("/api/participantes", methods=["GET"])
def api_participantes():
    return jsonify(get_all_participantes()), 200

@app.route("/api/salas", methods=["GET"])
def api_salas():
    return jsonify(get_all_salas()), 200

@app.route("/api/reservas", methods=["GET"])
def api_reservas():
    print("[REQ] /api/reservas")
    data = get_all_reservas()
    return jsonify(data), 200

@app.route("/api/sanciones", methods=["GET"])
def api_sanciones():
    return jsonify(get_all_sanciones()), 200

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/participantes", methods=["POST"])
def api_participantes_create():
    data = request.get_json(silent=True) or {}
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

@app.route("/api/salas", methods=["POST"])
def api_salas_create():
    data = request.get_json(silent=True) or {}
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

@app.route("/api/reservas", methods=["POST"])
def api_reservas_create():
    data = request.get_json(silent=True) or {}
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

@app.route("/api/sanciones", methods=["POST"])
def api_sanciones_create():
    data = request.get_json(silent=True) or {}
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

# --- GET single ---
@app.route("/api/participantes/<ci>", methods=["GET"])
def api_participante_one(ci):
    r = fetch_one(
        "SELECT ci,nombre,apellido,fecha_nac,genero FROM participante WHERE ci=%s",
        (ci,),
        ["ci","nombre","apellido","fecha_nac","genero"]
    )
    return (jsonify(r), 200) if r else (jsonify({"error":"No encontrado"}),404)

@app.route("/api/salas/<path:edificio>/<nombre_sala>", methods=["GET"])
def api_sala_one(edificio, nombre_sala):
    r = fetch_one(
        "SELECT nombre_sala,edificio,capacidad,tipo_sala FROM sala WHERE edificio=%s AND nombre_sala=%s",
        (edificio, nombre_sala),
        ["nombre_sala","edificio","capacidad","tipo_sala"]
    )
    return (jsonify(r),200) if r else (jsonify({"error":"No encontrado"}),404)

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

@app.route("/api/sanciones/<participante_ci>/<fecha_inicio>/<fecha_fin>", methods=["GET"])
def api_sancion_one(participante_ci, fecha_inicio, fecha_fin):
    r = fetch_one(
        "SELECT participante_ci,fecha_inicio,fecha_fin FROM sancion_cuenta WHERE participante_ci=%s AND fecha_inicio=%s AND fecha_fin=%s",
        (participante_ci, fecha_inicio, fecha_fin),
        ["participante_ci","fecha_inicio","fecha_fin"]
    )
    return (jsonify(r),200) if r else (jsonify({"error":"No encontrado"}),404)

# --- PUT update ---
@app.route("/api/participantes/<ci>", methods=["PUT"])
def api_participante_update(ci):
    data = request.get_json(silent=True) or {}
    ok, err = _execute_update(
        "UPDATE participante SET nombre=%s, apellido=%s, fecha_nac=%s, genero=%s WHERE ci=%s",
        (data.get("nombre"), data.get("apellido"), data.get("fecha_nac"), data.get("genero"), ci)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

@app.route("/api/salas/<path:edificio>/<nombre_sala>", methods=["PUT"])
def api_sala_update(edificio, nombre_sala):
    data = request.get_json(silent=True) or {}
    ok, err = _execute_update(
        "UPDATE sala SET capacidad=%s, tipo_sala=%s WHERE edificio=%s AND nombre_sala=%s",
        (data.get("capacidad"), data.get("tipo_sala"), edificio, nombre_sala)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

@app.route("/api/reservas/<int:id_reserva>", methods=["PUT"])
def api_reserva_update(id_reserva):
    data = request.get_json(silent=True) or {}
    ok, err = _execute_update(
        "UPDATE reserva SET nombre_sala=%s, edificio=%s, fecha=%s, id_turno=%s, estado=%s WHERE id_reserva=%s",
        (data.get("nombre_sala"), data.get("edificio"), data.get("fecha"),
         data.get("id_turno"), data.get("estado"), id_reserva)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

@app.route("/api/sanciones/<participante_ci>/<fecha_inicio>/<fecha_fin>", methods=["PUT"])
def api_sancion_update(participante_ci, fecha_inicio, fecha_fin):
    data = request.get_json(silent=True) or {}
    ok, err = _execute_update(
        "UPDATE sancion_cuenta SET fecha_inicio=%s, fecha_fin=%s WHERE participante_ci=%s AND fecha_inicio=%s AND fecha_fin=%s",
        (data.get("fecha_inicio_new") or fecha_inicio,
         data.get("fecha_fin_new") or fecha_fin,
         participante_ci, fecha_inicio, fecha_fin)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

# --- DELETE ---
@app.route("/api/participantes/<ci>", methods=["DELETE"])
def api_participante_delete(ci):
    ok, err = _execute_delete("DELETE FROM participante WHERE ci=%s", (ci,))
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)

@app.route("/api/salas/<path:edificio>/<nombre_sala>", methods=["DELETE"])
def api_sala_delete(edificio, nombre_sala):
    ok, err = _execute_delete("DELETE FROM sala WHERE edificio=%s AND nombre_sala=%s", (edificio, nombre_sala))
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)

@app.route("/api/reservas/<int:id_reserva>", methods=["DELETE"])
def api_reserva_delete(id_reserva):
    ok, err = _execute_delete("DELETE FROM reserva WHERE id_reserva=%s", (id_reserva,))
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)

@app.route("/api/sanciones/<participante_ci>/<fecha_inicio>/<fecha_fin>", methods=["DELETE"])
def api_sancion_delete(participante_ci, fecha_inicio, fecha_fin):
    ok, err = _execute_delete(
        "DELETE FROM sancion_cuenta WHERE participante_ci=%s AND fecha_inicio=%s AND fecha_fin=%s",
        (participante_ci, fecha_inicio, fecha_fin)
    )
    return (jsonify({"message":"Eliminado"}),200) if ok else (jsonify({"error":err or "No eliminado"}),400)

if __name__ == "__main__":
    # Ejecutar servicio (usar: py backend/services.py)
    app.run(host="0.0.0.0", port=5000, debug=True)