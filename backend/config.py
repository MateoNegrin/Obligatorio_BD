import os
import mysql.connector
from mysql.connector import Error

# Defaults (coinciden con init.sql)
DEFAULTS = {
    "DB_HOST": "127.0.0.1",  # Cambiar a nombre del servicio (ej: 'db') si corre dentro de Docker
    "DB_PORT": "3306",
    "DB_USER": "appuser",
    "DB_PASSWORD": "apppassword",
    "DB_NAME": "obligatorio"
}

def get_env(name):
    return os.getenv(name, DEFAULTS[name])

def get_connection():
    """Retorna conexión MySQL o None si falla."""
    try:
        conn = mysql.connector.connect(
            host=get_env("DB_HOST"),
            port=int(get_env("DB_PORT")),
            user=get_env("DB_USER"),
            password=get_env("DB_PASSWORD"),
            database=get_env("DB_NAME"),
            connection_timeout=5
        )
        if not conn.is_connected():
            return None
        return conn
    except Error as e:
        print(f"[DB] Error de conexión: {e}")
        return None

