import os
import json
import sqlite3
import threading
from queue import Queue, Empty
from datetime import datetime, timezone

from flask import Flask, render_template, g, Response, request, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt

# Config desde env
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
SQLITE_DB = os.environ.get("SQLITE_DB", "/data/measurements.db")
MQTT_TOPICS = [("cultivo/+/+/data", 0), ("cultivo/+/+/status", 0)]

SSE_TIMEOUT = 15

app = Flask(__name__)
CORS(app)

# --- DB helpers ---
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = sqlite3.connect(SQLITE_DB, check_same_thread=False)
        db.row_factory = sqlite3.Row
        g._database = db
    return db

def init_db():
    db = get_db()
    with db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts_ingest TEXT,
          ts_device TEXT,
          nodeId TEXT,
          seq INTEGER,
          sensor TEXT,
          value REAL,
          unit TEXT,
          nodeLat REAL,
          nodeLon REAL,
          nodeAlt REAL,
          status TEXT
        );
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_node_sensor_ts ON measurements(nodeId, sensor, ts_ingest);")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# --- SSE manager ---
clients = []

def push_event(evt: dict):
    raw = f"data: {json.dumps(evt)}\n\n"
    for q in clients[:]:
        try:
            q.put(raw, timeout=0.1)
        except Exception:
            try:
                clients.remove(q)
            except ValueError:
                pass

@app.route("/stream")
def stream():
    def gen(q: Queue):
        try:
            while True:
                try:
                    data = q.get(timeout=SSE_TIMEOUT)
                    yield data
                except Empty:
                    yield ": ping\n\n"
        finally:
            try:
                clients.remove(q)
            except Exception:
                pass

    q = Queue()
    clients.append(q)
    return Response(gen(q), mimetype="text/event-stream", headers={"Cache-Control": "no-cache"})

# --- MQTT callbacks ---
def mqtt_on_connect(client, userdata, flags, rc):
    print("MQTT connected rc=", rc)
    for topic, qos in MQTT_TOPICS:
        client.subscribe(topic, qos=qos)
        print("Subscribed to", topic)

def mqtt_on_message(client, userdata, msg):
    payload = None
    try:
        payload = msg.payload.decode()
        obj = json.loads(payload)
    except Exception as e:
        print("Invalid payload:", e, msg.topic, payload)
        return

    now_iso = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    nodeId = obj.get("nodeId") or obj.get("node_id") or "unknown"
    sensor = obj.get("sensor") or "unknown"
    value = obj.get("value")
    unit = obj.get("unit") or ""
    ts_device = obj.get("ts_device") or obj.get("ts") or None
    seq = obj.get("seq")
    lat = obj.get("nodeLat")
    lon = obj.get("nodeLon")
    alt = obj.get("nodeAlt")
    status = obj.get("status", "ok")

    db = get_db()
    with db:
        db.execute("""
            INSERT INTO measurements
            (ts_ingest, ts_device, nodeId, seq, sensor, value, unit, nodeLat, nodeLon, nodeAlt, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (now_iso, ts_device, nodeId, seq, sensor, value, unit, lat, lon, alt, status))

    evt = {
        "type": "measurement",
        "ts_ingest": now_iso,
        "nodeId": nodeId,
        "sensor": sensor,
        "value": value,
        "unit": unit,
        "nodeLat": lat,
        "nodeLon": lon,
        "status": status
    }
    push_event(evt)

def start_mqtt_thread():
    client = mqtt.Client()
    client.on_connect = mqtt_on_connect
    client.on_message = mqtt_on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    thread = threading.Thread(target=client.loop_forever, daemon=True)
    thread.start()
    print("MQTT thread started")

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/latest")
def api_latest():
    db = get_db()
    cur = db.execute("""
        SELECT m1.*
        FROM measurements m1
        JOIN (
            SELECT nodeId, sensor, MAX(ts_ingest) AS maxts
            FROM measurements
            GROUP BY nodeId, sensor
        ) m2 ON m1.nodeId = m2.nodeId AND m1.sensor = m2.sensor AND m1.ts_ingest = m2.maxts
    """)
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)

@app.route("/api/history")
def api_history():
    node = request.args.get("node")
    sensor = request.args.get("sensor")
    limit = int(request.args.get("limit", "200"))
    db = get_db()
    q = "SELECT * FROM measurements WHERE 1=1 "
    params = []
    if node:
        q += " AND nodeId = ?"
        params.append(node)
    if sensor:
        q += " AND sensor = ?"
        params.append(sensor)
    q += " ORDER BY ts_ingest DESC LIMIT ?"
    params.append(limit)
    cur = db.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)

# --- Startup ---
if __name__ == "__main__":
    with app.app_context():
        init_db()
    start_mqtt_thread()
    app.run(host="0.0.0.0", port=5000, threaded=True)
else:
    # When gunicorn imports app:app
    with app.app_context():
        init_db()
    start_mqtt_thread()
