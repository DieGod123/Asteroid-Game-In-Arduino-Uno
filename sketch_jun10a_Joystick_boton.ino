const int BUTTON_PIN = 4; // Pin digital para el botón adicional

void setup() {
  Serial.begin(9600);
pinMode(BUTTON_PIN, INPUT_PULLUP); // Configurar el pin del botón adicional como entrada con pull-up interno
}

void loop() {
  int x = analogRead(A0);  // Leer posición X del joystick
  int buttonState = digitalRead(4);  // Leer estado del botón

  if (x < 400) {
    Serial.println("izquierda");
  } else if (x > 600) {
    Serial.println("derecha");
  }

  if (!buttonState) {
    Serial.println("disparar");
  }

  delay(100);  // Pequeña pausas
}