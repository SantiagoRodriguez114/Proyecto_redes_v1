import json
import sqlite3
import threading
import time
from datetime import datetime

from flask import Flask, render_template, g
import paho.mqtt.client as mqtt

# --- Flask setup ---
app = Flask(__name__)
DATABASE = "data.db"

# --- SQLite helpers ---
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

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
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
            """
        )
        db.commit()

def insert_data(db, data):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO sensor_data (ts_device, nodeId, sensor, value, unit, nodeLat, nodeLon, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("ts_device"),
            data.get("nodeId"),
            data.get("sensor"),
            data.get("value"),
            data.get("unit"),
            data.get("nodeLat"),
            data.get("nodeLon"),
            data.get("status"),
        ),
    )
    db.commit()

# --- MQTT setup ---
MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "cultivo/loteA/+/data"

def mqtt_on_connect(client, userdata, flags, rc):
    print(f"MQTT conectado con código {rc}")
    client.subscribe(MQTT_TOPIC)

def mqtt_on_message(client, userdata, msg):
    with app.app_context():  # ← CORRECCIÓN CLAVE
        try:
            data = json.loads(msg.payload.decode())
            db = get_db()
            insert_data(db, data)
            print(f"[MQTT] Guardado en DB: {data}")
        except Exception as e:
            print(f"Error al procesar mensaje MQTT: {e}")

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = mqtt_on_connect
    client.on_message = mqtt_on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# --- Flask routes ---
@app.route("/")
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM sensor_data ORDER BY id DESC LIMIT 50"
    )
    rows = cursor.fetchall()
    return render_template("index.html", rows=rows)

# --- Main ---
if __name__ == "__main__":
    init_db()
    threading.Thread(target=start_mqtt, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
