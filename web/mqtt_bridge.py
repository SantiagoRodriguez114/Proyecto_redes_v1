import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "cultivo/loteA/+/data"

def start_bridge(socketio):
    client = mqtt.Client()

    def on_connect(client, userdata, flags, rc):
        print("[BRIDGE] Conectado a MQTT:", rc)
        client.subscribe(MQTT_TOPIC)

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            print("[BRIDGE] MQTT → WS:", data)

            # Enviar el dato al navegador en tiempo real
            socketio.emit("nuevo_dato", data)

        except Exception as e:
            print("[BRIDGE] Error:", e)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
