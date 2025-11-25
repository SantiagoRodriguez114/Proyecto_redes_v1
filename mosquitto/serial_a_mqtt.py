#!/usr/bin/env python3
import serial, json, time, argparse
import paho.mqtt.client as mqtt
from datetime import datetime

p = argparse.ArgumentParser(description="Publicador MQTT desde ESP32 via Serial")
p.add_argument("--serial", required=True, help="Puerto serial, ej: /dev/ttyUSB0")
p.add_argument("--baud", type=int, default=115200)
p.add_argument("--broker", required=True, help="IP del servidor MQTT")
p.add_argument("--node-id", default="nodeA")
args = p.parse_args()

client = mqtt.Client(f"pub-{args.node_id}")
client.connect(args.broker, 1883, 60)
client.loop_start()

ser = serial.Serial(args.serial, args.baud, timeout=1)
print(f"[INFO] Enviando datos desde {args.node_id} hacia {args.broker}")

while True:
    line = ser.readline().decode("utf-8", "ignore").strip()
    if not line:
        continue
    try:
        payload = json.loads(line)
    except:
        payload = {"_raw": line}

    payload["_meta"] = {
        "node_id": args.node_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    topic = f"agro/{args.node_id}/telemetry"
    client.publish(topic, json.dumps(payload))
    print(f"[PUB {topic}] {payload}")
