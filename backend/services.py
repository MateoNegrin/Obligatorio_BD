import sys
import os
# Agregar directorio padre al path si no está
if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from flask import jsonify
from backend.app import app

@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok"}), 200

from backend.routes import salas, reservas, participantes, sanciones, consultas

if __name__ == "__main__":
    print("=== Rutas registradas ===")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint:30s} {rule.rule}")
    print("=========================")
    app.run(host="0.0.0.0", port=5000, debug=True)