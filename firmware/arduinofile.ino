// 13,12,14,27,26,25,33
const int SENSOR_PINS[4] = {13,12,14,27};
const int NUM_SENSORS = 4;

int lastSensorTouched = -1;

void setup() {
  Serial.begin(9600); 

  // Configuración para SENSOR ACTIVO ALTO:
  // PULLDOWN para mantener el pin en LOW por defecto.
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(SENSOR_PINS[i], INPUT_PULLDOWN); // <-- CAMBIO 1
  }
  
  Serial.println("ESP32 listo. (Versión definitiva para sensor Activo Alto)");
}

void loop() {
  bool anySensorTouched = false;
  
  for (int i = 0; i < NUM_SENSORS; i++) {
    // Lógica para SENSOR ACTIVO ALTO:
    // Buscar una señal HIGH cuando se presiona.
    if (digitalRead(SENSOR_PINS[i]) == HIGH) { // <-- CAMBIO 2
      
      if (i != lastSensorTouched) {
        Serial.println(i);
        Serial.flush();
        lastSensorTouched = i;
      }
      anySensorTouched = true;
      break; 
    }
  }

  if (!anySensorTouched) {
    if (lastSensorTouched != -1) {
        Serial.println("reset"); 
        Serial.flush();
    }
    lastSensorTouched = -1;
  }
  
  delay(100); 
}