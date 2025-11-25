#define RAIN_PIN 34   // A0 del módulo de lluvia va a GPIO 34

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Nodo de Lluvia listo");
}

void loop() {
  int rainValue = analogRead(RAIN_PIN);

  // Crear JSON
  String json = "{";
  json += "\"lluvia\":" + String(rainValue);
  json += "}";

  Serial.println(json);

  delay(2000);
}
