import os
import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Definición de 4 nodos con coordenadas ejemplo
nodes = [
    {"nodeId": "node01", "lat": 4.6100, "lon": -74.0700},
    {"nodeId": "node02", "lat": 4.6150, "lon": -74.0650},
    {"nodeId": "node03", "lat": 4.6200, "lon": -74.0600},
    {"nodeId": "node04", "lat": 4.6250, "lon": -74.0550},
]

sensors = [
    {"sensor": "soil_moisture", "unit": "%", "min": 20, "max": 60},
    {"sensor": "temperature", "unit": "°C", "min": 15, "max": 35},
    {"sensor": "solar_radiation", "unit": "W/m2", "min": 0, "max": 1200},
    {"sensor": "ph", "unit": "pH", "min": 5.5, "max": 7.5},
]

seq = 0

def publish_node(n):
    global seq
    for s in sensors:
        seq += 1
        now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        # small random walk toward a base
        base = (s["min"] + s["max"]) / 2
        noise = random.uniform(- (s["max"]-s["min"]) * 0.15, (s["max"]-s["min"]) * 0.15)
        val = round(max(s["min"], min(s["max"], base + noise)), 2)
        payload = {
            "ts_device": now,
            "nodeId": n["nodeId"],
            "seq": seq,
            "sensor": s["sensor"],
            "value": val,
            "unit": s["unit"],
            "nodeLat": n["lat"],
            "nodeLon": n["lon"],
            "status": "ok"
        }
        topic = f"cultivo/loteA/{n['nodeId']}/data"
        client.publish(topic, json.dumps(payload), qos=0)
        print("pub", topic, payload)

if __name__ == "__main__":
    try:
        while True:
            for n in nodes:
                publish_node(n)
                time.sleep(1.5)  # breve entre nodos
            # cada ciclo espera ~5-8s
            time.sleep(3)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
