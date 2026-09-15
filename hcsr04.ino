// ==========================================
// ESP-12F / ESP8266 + HC-SR04
//
// VCC  -> 5V
// TRIG -> D1 (GPIO5)
// ECHO -> D2 (GPIO4)
// GND  -> GND
//
// Output:
// {"measurement":1,"duration":154,"distance":2.64}
// ==========================================

#define TRIG_PIN D1
#define ECHO_PIN D2

unsigned long duration;
float distance;

unsigned long measurement = 0;

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);

  delay(500);
}

void loop() {

  // Mengirim pulsa trigger
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  // Membaca durasi Echo
  duration = pulseIn(ECHO_PIN, HIGH, 30000);

  // Menambah nomor pengukuran
  measurement++;

  // Jika pembacaan berhasil
  if (duration > 0) {

    // Menghitung jarak dalam cm
    distance = (duration * 0.0343) / 2.0;

    // Output JSON
    Serial.print("{");
    Serial.print("\"measurement\":");
    Serial.print(measurement);

    Serial.print(",\"duration\":");
    Serial.print(duration);

    Serial.print(",\"distance\":");
    Serial.print(distance, 2);

    Serial.println("}");

  } else {

    // Jika pembacaan gagal
    Serial.print("{");
    Serial.print("\"measurement\":");
    Serial.print(measurement);

    Serial.print(",\"duration\":null");

    Serial.print(",\"distance\":null");

    Serial.println("}");
  }

  // Interval pengukuran 500 ms
  delay(500);
}