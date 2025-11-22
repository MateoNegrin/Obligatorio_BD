from flask import jsonify, request
from backend.app import app
from backend.utils.dbUtils import fetch_all, fetch_one, _execute_insert, _execute_update, _execute_delete
from backend.utils.sanitize import sanitize_fields

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

# Helper local para parametrizar únicamente LIMIT de forma segura (entero)
def fetch_param(sql, params, cols):
    if params:
        # Solo se espera un entero para LIMIT
        limit = int(params[0])
        final_sql = sql.replace("%s", str(limit))
    else:
        final_sql = sql
    return fetch_all(final_sql, cols)

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

