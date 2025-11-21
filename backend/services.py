from mysql.connector import Error  # corregido
from config import get_connection

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

def fetch_all(query, cols):
    """Helper genérico para SELECT *."""
    conn = get_connection()
    if not conn:
        print("[DB] Conexión fallida en fetch_all.")
        return []
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(zip(cols, r)) for r in rows]
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
        "SELECT id_reserva, nombre_sala, edificio, fecha, id_turno, estado FROM reserva",
        ["id_reserva", "nombre_sala", "edificio", "fecha", "id_turno", "estado"]
    )

def get_all_sanciones():
    return fetch_all(
        "SELECT participante_ci, fecha_inicio, fecha_fin FROM sancion_cuenta",
        ["participante_ci", "fecha_inicio", "fecha_fin"]
    )