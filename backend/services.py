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

# Endpoints Flask
app = Flask(__name__)
CORS(app)  # habilita CORS para peticiones desde file:// y http://

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

if __name__ == "__main__":
    # Ejecutar servicio (usar: py backend/services.py)
    app.run(host="0.0.0.0", port=5000, debug=True)