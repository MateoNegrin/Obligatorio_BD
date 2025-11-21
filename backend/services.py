from mysql.connector import Error
from config import get_connection
from flask import Flask, jsonify 
from flask_cors import CORS  

def ping():
    """Prueba simple de conexión y SELECT 1."""
    conn = get_connection()
    if not conn:
        print("[DB] Conexión fallida.")
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchall()
        cur.close()
        conn.close()
        print("[DB] OK.")
        return True
    except Error as e:
        print(f"[DB] Error en ping: {e}")
        return False

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
    """Helper genérico para SELECT *."""
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

def get_all_reservas():
    return fetch_all(
        """SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha,
                  t.hora_inicio, t.hora_fin, r.estado
           FROM reserva r
           JOIN turno t ON r.id_turno = t.id_turno""",
        ["id_reserva", "nombre_sala", "edificio", "fecha", "hora_inicio", "hora_fin", "estado"]
    )

def get_all_sanciones():
    return fetch_all(
        "SELECT participante_ci, fecha_inicio, fecha_fin FROM sancion_cuenta",
        ["participante_ci", "fecha_inicio", "fecha_fin"]
    )

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
    return jsonify(get_all_reservas()), 200

@app.route("/api/sanciones", methods=["GET"])
def api_sanciones():
    return jsonify(get_all_sanciones()), 200

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Ejecutar servicio (usar: py backend/services.py)
    app.run(host="0.0.0.0", port=5000, debug=True)