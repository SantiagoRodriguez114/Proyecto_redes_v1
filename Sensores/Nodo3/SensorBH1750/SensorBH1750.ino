#include <Wire.h>
#include <BH1750.h>

BH1750 lightMeter;

void setup() {
  Serial.begin(115200);
  delay(500);

  // Inicializar bus I2C
  Wire.begin(21, 22);   // SDA = 21, SCL = 22

  // Inicializar sensor BH1750
  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("BH1750 listo");
  } else {
    Serial.println("Error iniciando BH1750");
  }
}

void loop() {
  float lux = lightMeter.readLightLevel();  // Luz en lux

  // Crear JSON para este nodo
  String json = "{";
  json += "\"luz\":" + String(lux, 1);
  json += "}";

  Serial.println(json);

  delay(2000);
}
