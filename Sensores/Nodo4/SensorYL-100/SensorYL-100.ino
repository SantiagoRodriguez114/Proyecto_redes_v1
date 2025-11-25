#define SOIL_PIN 35   // A0 del módulo YL-100

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Nodo 4 - Humedad de Suelo YL-100 listo");
}

void loop() {
  int soil = analogRead(SOIL_PIN);

  // Crear JSON
  String json = "{";
  json += "\"humedad_suelo\":" + String(soil);
  json += "}";

  Serial.println(json);

  delay(2000);
}
