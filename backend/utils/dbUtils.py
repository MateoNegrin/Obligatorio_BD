from mysql.connector import Error
from backend.config import get_connection
from backend.utils.sanitize import formatDate

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
        return [ { cols[i]: formatDate(row[i]) for i in range(len(cols)) } for row in rows ]
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
        return { cols[i]: formatDate(row[i]) for i in range(len(cols)) }
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
        return [{cols[i]: formatDate(r[i]) for i in range(len(cols))} for r in rows]
    except Error as e:
        print(f"[DB] Error en fetch_param: {e}")
        return []

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