from mysql.connector import Error
from config import get_connection
from flask import Flask, jsonify, request
from flask_cors import CORS
import re

def _to_json_safe(v):
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

def fetch_param(query, params, cols):
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [{cols[i]: _to_json_safe(r[i]) for i in range(len(cols))} for r in rows]
    except Error as e:
        print(f"[DB] Error en fetch_param: {e}")
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

CONSULTAS = {
    "salas_top": {
        "sql": "SELECT nombre_sala, COUNT(*) AS reservas FROM reserva GROUP BY nombre_sala ORDER BY reservas DESC LIMIT %s",
        "cols": ["nombre_sala","reservas"],
        "limit_default": 3
    },
    "turnos_top": {
        "sql": """SELECT r.id_turno, t.hora_inicio, t.hora_fin, COUNT(*) AS reservas
                  FROM reserva r JOIN turno t ON t.id_turno = r.id_turno
                  GROUP BY r.id_turno, t.hora_inicio, t.hora_fin
                  ORDER BY reservas DESC LIMIT %s""",
        "cols": ["id_turno","hora_inicio","hora_fin","reservas"],
        "limit_default": 3
    },
    "promedio_participantes_sala": {
        "sql": """SELECT x.nombre_sala, AVG(x.suma) AS promedio_participantes
                  FROM (
                    SELECT r.nombre_sala, r.id_reserva, COUNT(*) AS suma
                    FROM reserva r JOIN reserva_cuenta rc ON r.id_reserva = rc.id_reserva
                    GROUP BY r.nombre_sala, r.id_reserva
                  ) x
                  GROUP BY x.nombre_sala""",
        "cols": ["nombre_sala","promedio_participantes"]
    },
    "reservas_por_carrera_facultad": {
        "sql": """SELECT cp.nombre_programa, f.nombre AS facultad, COUNT(rc.id_reserva) AS reservas
                  FROM reserva_cuenta rc
                  JOIN datos_cuenta dc ON rc.participante_ci = dc.ci
                  JOIN cuenta_programa_academico cp ON dc.email = cp.email
                  JOIN programa_academico pa ON pa.nombre_programa = cp.nombre_programa
                  JOIN facultad f ON f.id_facultad = pa.id_facultad
                  GROUP BY cp.nombre_programa, f.nombre""",
        "cols": ["nombre_programa","facultad","reservas"]
    },
    "ocupacion_por_edificio": {
        "sql": """SELECT e.nombre_edificio,
                         COUNT(r.id_reserva)/COUNT(r.nombre_sala) AS porcentaje_ocupacion
                  FROM reserva r JOIN sala s ON r.nombre_sala = s.nombre_sala AND r.edificio = s.edificio
                  RIGHT JOIN edificio e ON e.nombre_edificio = s.edificio
                  WHERE r.fecha = CURDATE() AND r.id_turno = (
                      SELECT id_turno FROM turno
                      WHERE hora_inicio < CURTIME() AND hora_fin > CURTIME()
                      LIMIT 1
                  )
                  GROUP BY e.nombre_edificio""",
        "cols": ["nombre_edificio","porcentaje_ocupacion"]
    },
    "reservas_asistencias": {
        "sql": """SELECT dc.rol, pa.tipo,
                         COUNT(r.id_reserva) AS reservas,
                         COUNT(CASE WHEN rc.asistencia = TRUE THEN 1 END) AS asistencias
                  FROM reserva_cuenta rc
                  JOIN reserva r ON rc.id_reserva = r.id_reserva
                  JOIN datos_cuenta dc ON rc.participante_ci = dc.ci
                  JOIN cuenta_programa_academico cpa ON dc.email = cpa.email
                  JOIN programa_academico pa ON pa.nombre_programa = cpa.nombre_programa
                  GROUP BY dc.rol, pa.tipo""",
        "cols": ["rol","tipo","reservas","asistencias"]
    },
    "sanciones_por_rol_tipo": {
        "sql": """SELECT dc.rol, pa.tipo, COUNT(*) AS sanciones
                  FROM sancion_cuenta sc
                  JOIN datos_cuenta dc ON dc.ci = sc.participante_ci
                  JOIN cuenta_programa_academico cpa ON cpa.email = dc.email
                  JOIN programa_academico pa ON pa.nombre_programa = cpa.nombre_programa
                  GROUP BY dc.rol, pa.tipo""",
        "cols": ["rol","tipo","sanciones"]
    },
    "porcentaje_utilizacion": {
        "sql": """SELECT
                    (COUNT(CASE WHEN estado IN ('finalizada','activa') THEN 1 END) /
                     NULLIF(COUNT(CASE WHEN estado IN ('cancelada','sin asistencia') THEN 1 END),0)
                    ) AS ratio_utilizadas_vs_no
                  FROM reserva""",
        "cols": ["ratio_utilizadas_vs_no"]
    },
    "proporcion_alumnas": {
        "sql": """SELECT pa.nombre_programa, f.nombre AS facultad,
                         COUNT(CASE WHEN genero='femenino' THEN 1 END)/COUNT(*) AS proporcion_alumnas
                  FROM participante p
                  JOIN datos_cuenta dc ON p.ci = dc.ci
                  JOIN cuenta_programa_academico cpa ON cpa.email = dc.email
                  JOIN programa_academico pa ON pa.nombre_programa = cpa.nombre_programa
                  JOIN facultad f ON f.id_facultad = pa.id_facultad
                  WHERE dc.rol = 'alumno'
                  GROUP BY pa.nombre_programa, f.nombre""",
        "cols": ["nombre_programa","facultad","proporcion_alumnas"]
    },
    "reservas_por_genero": {
        "sql": """SELECT p.genero, COUNT(*) AS reservas
                  FROM participante p
                  JOIN reserva_cuenta rc ON p.ci = rc.participante_ci
                  GROUP BY p.genero""",
        "cols": ["genero","reservas"]
    },
    "edad_promedio_por_edificio": {
        "sql": """SELECT e.nombre_edificio,
                         AVG(TIMESTAMPDIFF(YEAR, p.fecha_nac, CURDATE())) AS edad_promedio
                  FROM edificio e
                  JOIN reserva r ON e.nombre_edificio = r.edificio
                  JOIN reserva_cuenta rc ON r.id_reserva = rc.id_reserva
                  JOIN participante p ON p.ci = rc.participante_ci
                  GROUP BY e.nombre_edificio""",
        "cols": ["nombre_edificio","edad_promedio"]
    }
}

# Endpoints
app = Flask(__name__)
CORS(app)  

#Get all
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

#Get one
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

@app.route("/api/salas/<path:edificio>/<nombre_sala>", methods=["PUT"])
def api_sala_update(edificio, nombre_sala):
    data = request.get_json(silent=True) or {}
    sanitize_fields(data, ["capacidad","tipo_sala"])  # capacidad numérica se ignora si no string
    ok, err = _execute_update(
        "UPDATE sala SET capacidad=%s, tipo_sala=%s WHERE edificio=%s AND nombre_sala=%s",
        (data.get("capacidad"), data.get("tipo_sala"), edificio, nombre_sala)
    )
    return (jsonify({"message":"Actualizado"}),200) if ok else (jsonify({"error":err or "No actualizado"}),400)

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

#Consultas parametrizadas
@app.route("/api/consultas/<clave>", methods=["GET"])
def api_consulta(clave):
    conf = CONSULTAS.get(clave)
    if not conf:
        return jsonify({"error":"Consulta inválida"}), 400
    if "%s" in conf["sql"]:
        try:
            limit = int(request.args.get("limit", conf.get("limit_default", 3)))
        except ValueError:
            limit = conf.get("limit_default", 3)
        data = fetch_param(conf["sql"], (limit,), conf["cols"])
    else:
        data = fetch_param(conf["sql"], (), conf["cols"])
    return jsonify(data), 200

def sanitize_input(s: str):
    if not isinstance(s, str):
        return s
    return re.sub(r"[\'\"`;%#\\]", "", s)

def sanitize_fields(data: dict, field_names):
    for k in field_names:
        if k in data and isinstance(data[k], str):
            data[k] = sanitize_input(data[k])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)