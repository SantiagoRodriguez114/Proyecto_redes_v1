import json
import sqlite3
import threading
from flask import Flask, render_template, g, jsonify
from flask_socketio import SocketIO

import paho.mqtt.client as mqtt
import mqtt_bridge  # nuevo archivo

# ---------------------------------------------------
# FLASK + SOCKET.IO
# ---------------------------------------------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE = "data.db"


# ============================
# GESTIÓN DE BASE DE DATOS
# ============================

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def ensure_database():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_device TEXT,
            nodeId TEXT,
            sensor TEXT,
            value REAL,
            unit TEXT,
            nodeLat REAL,
            nodeLon REAL,
            status TEXT
        )
    """)
    db.commit()
    db.close()
    print("Base de datos lista.")


def insert_data(data):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO sensor_data (ts_device, nodeId, sensor, value, unit, nodeLat, nodeLon, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("ts_device"),
            data.get("nodeId"),
            data.get("sensor"),
            data.get("value"),
            data.get("unit"),
            data.get("nodeLat"),
            data.get("nodeLon"),
            data.get("status"),
        ))
        db.commit()
    except Exception as e:
        print("Error insertando:", e)


# ============================
# MQTT → BASE DE DATOS
# ============================

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "agro/+/telemetry"


def on_connect(client, userdata, flags, rc):
    print("MQTT conectado:", rc)
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        raw = json.loads(msg.payload.decode())

        data = {
            "ts_device": raw["_meta"]["timestamp"],
            "nodeId": raw["_meta"]["node_id"],
            "sensor": "temp",
            "value": raw["temp"],
            "unit": "C",
            "nodeLat": None,
            "nodeLon": None,
            "status": "OK"
        }

        with app.app_context():
            insert_data(data)


        print("[MQTT→DB] Guardado:", data)

    except Exception as e:
        print("Error MQTT→DB:", e)


def start_mqtt_background():
    def mqtt_thread():
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()

    threading.Thread(target=mqtt_thread, daemon=True).start()


# ============================
# RUTAS
# ============================

@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    return render_template("index.html", rows=rows)


@app.route("/api/data")
def api_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 100")
    data = [dict(row) for row in cursor.fetchall()]
    return jsonify(data)


# ============================
# INICIO GLOBAL
# ============================

ensure_database()
start_mqtt_background()
mqtt_bridge.start_bridge(socketio)

print("Flask con WebSocket iniciado correctamente.")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
