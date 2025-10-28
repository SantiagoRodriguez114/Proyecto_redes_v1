import json
import sqlite3
import threading
from flask import Flask, render_template, g, jsonify
import paho.mqtt.client as mqtt

# --- Configuración básica ---
app = Flask(__name__)
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
    """Crea la base de datos y tabla si no existen."""
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
    print("Base de datos verificada / creada correctamente.")

def insert_data(data):
    """Inserta un registro en la tabla sensor_data."""
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
        print(f"Error insertando en la base de datos: {e}")

# ============================
# MQTT CLIENTE
# ============================

MQTT_BROKER = "mosquitto"  # nombre del servicio en docker-compose
MQTT_PORT = 1883
MQTT_TOPIC = "cultivo/loteA/+/data"

def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        with app.app_context():
            insert_data(data)
        print(f"[MQTT] Guardado en DB: {data}")
    except Exception as e:
        print(f"Error procesando mensaje MQTT: {e}")

def start_mqtt_background():
    """Inicia el hilo MQTT incluso si Flask corre bajo Gunicorn."""
    def mqtt_thread():
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            print("Cliente MQTT iniciado correctamente.")
            client.loop_forever()
        except Exception as e:
            print(f"Error conectando al broker MQTT: {e}")

    threading.Thread(target=mqtt_thread, daemon=True).start()

# ============================
# RUTAS FLASK
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
# INICIALIZACIÓN GLOBAL
# ============================

# Esto se ejecuta tanto con Gunicorn como con python app.py
ensure_database()
start_mqtt_background()
print("Flask app inicializada correctamente.")
