#include <Arduino.h>
#include <DHT.h>

// ===== CONFIGURACIÓN DEL SENSOR =====
#define DHTPIN 4        // Tu pin de datos OUT va aquí
#define DHTTYPE DHT22   // Tipo de sensor (DHT22)

DHT dht(DHTPIN, DHTTYPE);

// ===== SETUP =====
void setup() {
  Serial.begin(115200);   // Comunicación con la PC
  dht.begin();            // Iniciar sensor
  delay(2000);
  Serial.println("ESP32 lista con DHT22");
}

// ===== LOOP =====
void loop() {
  // Leer temperatura y humedad
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println("{\"error\":\"fallo en DHT22\"}");
  } else {
    // Crear JSON
    String json = "{";
    json += "\"temp\":" + String(temp, 1) + ",";
    json += "\"humedad\":" + String(hum, 1);
    json += "}";
    
    // Enviar por Serial
    Serial.println(json);
  }

  delay(2000); // Cada 2 segundos
}
