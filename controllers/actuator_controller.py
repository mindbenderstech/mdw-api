# controllers/actuator_controller.py
import platform
import psutil
import time
from flask import Blueprint, jsonify
from db import get_db_connection

actuator_controller = Blueprint('actuator_controller', __name__)

start_time = time.time()

@actuator_controller.route('/actuator/health', methods=['GET'])
def actuator_health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({"status": "UP", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "DOWN", "db": "disconnected", "error": str(e)}), 500


@actuator_controller.route('/actuator/info', methods=['GET'])
def actuator_info():
    return jsonify({
        "app": {
            "name": "MediaWorld API",
            "version": "1.0.0"
        },
        "python": platform.python_version(),
        "platform": platform.system()
    })


@actuator_controller.route('/actuator/metrics', methods=['GET'])
def actuator_metrics():
    uptime = time.time() - start_time
    return jsonify({
        "uptime_seconds": round(uptime, 2),
        "memory_usage_mb": round(psutil.virtual_memory().used / (1024 * 1024), 2),
        "cpu_percent": psutil.cpu_percent(interval=0.5)
    })
