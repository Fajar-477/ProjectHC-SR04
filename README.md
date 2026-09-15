Tentu. Berikut README yang bisa langsung Anda gunakan untuk proyek **ESP-12F + HC-SR04 → JSON → Python melalui Serial**. Saya buat dengan struktur yang cocok untuk repository GitHub dan dokumentasi penelitian.

# ESP-12F + HC-SR04 JSON Serial Reader

Sistem pengukuran jarak berbasis **ESP-12F (ESP8266)** dan sensor ultrasonik **HC-SR04** dengan komunikasi serial dalam format **JSON**. Data hasil pengukuran dikirim oleh ESP-12F melalui port serial dan dibaca serta divalidasi menggunakan Python.

Proyek ini dirancang sebagai dasar untuk **akuisisi data sensor, validasi data, penyimpanan dataset, dan pengembangan sistem instrumentasi berbasis IoT/AI**.

---

## 1. Fitur

* Pengukuran jarak menggunakan sensor ultrasonik HC-SR04.
* Mikrokontroler ESP-12F berbasis ESP8266.
* Output sensor dalam format JSON.
* Komunikasi data melalui USB-to-Serial.
* Pembacaan JSON secara real-time menggunakan Python.
* Validasi struktur JSON menggunakan `json.loads()`.
* Validasi hubungan antara durasi Echo dan jarak.
* Penomoran setiap pengukuran menggunakan `measurement`.
* Penanganan pembacaan sensor yang gagal.
* Dapat dikembangkan untuk penyimpanan data ke JSON, CSV, database, atau sistem AI.

---

## 2. Arsitektur Sistem

```text
                ┌─────────────────┐
                │    HC-SR04      │
                │ Ultrasonic Sensor│
                └────────┬────────┘
                         │
                         │ TRIG / ECHO
                         ▼
                ┌─────────────────┐
                │     ESP-12F     │
                │    ESP8266      │
                └────────┬────────┘
                         │
                    USB Serial
                    COM7 / 115200
                         │
                         ▼
                ┌─────────────────┐
                │     Python      │
                │   JSON Reader   │
                └────────┬────────┘
                         │
                         ▼
              JSON Validation / Analysis
```

---

## 3. Hardware

### Komponen

| Komponen                   |     Jumlah |
| -------------------------- | ---------: |
| ESP-12F / ESP8266          |          1 |
| HC-SR04                    |          1 |
| USB-to-TTL / USB-to-Serial |          1 |
| Resistor 1 kΩ              |          1 |
| Resistor 2 kΩ              |          1 |
| Kabel jumper               | Secukupnya |
| Catu daya 5 V              |          1 |

---

## 4. Wiring HC-SR04

Konfigurasi pin:

| HC-SR04 | ESP-12F                            |
| ------- | ---------------------------------- |
| VCC     | 5 V                                |
| TRIG    | D1 / GPIO5                         |
| ECHO    | D2 / GPIO4 melalui voltage divider |
| GND     | GND                                |

### Voltage Divider ECHO

HC-SR04 dapat menghasilkan sinyal ECHO sekitar 5 V, sedangkan GPIO ESP8266 menggunakan level logika 3,3 V.

Gunakan pembagi tegangan:

```text
HC-SR04 ECHO
      │
     1 kΩ
      │
      ├────────── D2 / GPIO4
      │
     2 kΩ
      │
     GND
```

Tegangan pada GPIO:

```text
Vout = 5 × (2 kΩ / (1 kΩ + 2 kΩ))
     ≈ 3.33 V
```

**Jangan menghubungkan sinyal ECHO 5 V secara langsung ke GPIO ESP8266.**

---

## 5. Konfigurasi Arduino IDE

Install **ESP8266 Arduino Core** melalui Boards Manager.

Kemudian pilih:

```text
Tools
→ Board
→ ESP8266 Boards
→ Generic ESP8266 Module
```

Untuk modul ESP-12F bare module, `Generic ESP8266 Module` digunakan sebagai konfigurasi umum.

Contoh konfigurasi:

```text
Board        : Generic ESP8266 Module
Upload Speed : 115200
CPU Frequency: 80 MHz
Flash Size   : 4 MB
Port         : COM7
```

Sesuaikan nomor COM dengan perangkat yang digunakan pada komputer.

---

# 6. Program ESP-12F

Program berikut membaca HC-SR04 dan mengirimkan hasil pengukuran sebagai JSON melalui Serial.

```cpp
#define TRIG_PIN D1
#define ECHO_PIN D2

unsigned long duration;
float distance;

unsigned long measurement = 0;

const unsigned long measurementInterval = 500;

void setup() {

  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  digitalWrite(TRIG_PIN, LOW);

  delay(500);
}

void loop() {

  // Trigger HC-SR04
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  // Membaca durasi Echo
  duration = pulseIn(ECHO_PIN, HIGH, 30000);

  // Menambah nomor pengukuran
  measurement++;

  // Pembacaan berhasil
  if (duration > 0) {

    // Menghitung jarak
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

  }

  // Pembacaan gagal
  else {

    Serial.print("{");

    Serial.print("\"measurement\":");
    Serial.print(measurement);

    Serial.print(",\"duration\":null");

    Serial.print(",\"distance\":null");

    Serial.println("}");
  }

  delay(measurementInterval);
}
```

---

# 7. Format Data

ESP-12F menghasilkan satu JSON object pada setiap pengukuran.

Contoh:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

Parameter:

| Parameter     | Tipe    | Keterangan                         |
| ------------- | ------- | ---------------------------------- |
| `measurement` | Integer | Nomor pengukuran                   |
| `duration`    | Integer | Durasi pulsa Echo dalam mikrodetik |
| `distance`    | Float   | Jarak dalam cm                     |

Output tersebut menggunakan konsep **NDJSON (Newline Delimited JSON)** atau **JSON Lines**, karena setiap baris merupakan satu objek JSON.

Contoh:

```text
{"measurement":1,"duration":154,"distance":2.64}
{"measurement":2,"duration":156,"distance":2.68}
{"measurement":3,"duration":153,"distance":2.62}
```

---

# 8. Rumus Pengukuran Jarak

Jarak dihitung berdasarkan waktu tempuh gelombang ultrasonik.

Persamaan:

$$
d = \frac{v t}{2}
$$

dengan:

* \(d\) = jarak dalam cm
* \(v\) = kecepatan suara = 0,0343 cm/µs
* \(t\) = durasi Echo dalam µs
* faktor 2 berasal dari perjalanan gelombang pergi dan kembali

Program menggunakan:

```cpp
distance = (duration * 0.0343) / 2.0;
```

Sebagai contoh:

```text
duration = 1606 µs
```

maka:

$$
d =
\frac{1606 \times 0,0343}{2}
$$

$$
d \approx 27,54\text{ cm}
$$

Sehingga ESP-12F menghasilkan:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

---

# 9. Python JSON Reader

Python digunakan untuk membaca data JSON secara langsung dari port serial ESP-12F.

Install library:

```bash
pip install pyserial
```

atau:

```bash
python -m pip install pyserial
```

Buat file:

```text
read_hcsr04.py
```

Gunakan program:

```python
import serial
import json
import time

PORT = "COM7"
BAUDRATE = 115200

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        timeout=1
    )

    time.sleep(2)

    ser.reset_input_buffer()

except serial.SerialException as error:

    print("Gagal membuka serial port.")
    print("Error:", error)
    exit()


print("====================================")
print("ESP-12F + HC-SR04")
print("JSON Serial Reader")
print("====================================")
print("Port    :", PORT)
print("Baudrate:", BAUDRATE)
print("Menunggu data...\n")


try:

    while True:

        raw_data = ser.readline()

        if not raw_data:
            continue

        line = raw_data.decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        # Memastikan baris terlihat seperti JSON
        if not line.startswith("{") or not line.endswith("}"):
            continue

        print("Data Serial:")
        print(line)

        try:

            # Parse JSON
            data = json.loads(line)

            print("JSON VALID")

            measurement = data["measurement"]
            duration = data["duration"]
            distance = data["distance"]

            print("Measurement :", measurement)
            print("Duration    :", duration, "us")
            print("Distance    :", distance, "cm")

            # Validasi perhitungan
            calculated_distance = (
                duration * 0.0343
            ) / 2

            difference = abs(
                distance - calculated_distance
            )

            print(
                "Jarak hasil perhitungan Python :",
                round(calculated_distance, 2),
                "cm"
            )

            print(
                "Selisih                        :",
                round(difference, 4),
                "cm"
            )

            print("------------------------------------")

        except json.JSONDecodeError:

            print("JSON TIDAK VALID")

        except KeyError as error:

            print(
                "Key JSON tidak ditemukan:",
                error
            )

except KeyboardInterrupt:

    print("\nProgram dihentikan.")

finally:

    ser.close()

    print("Serial port ditutup.")
```

---

# 10. Menjalankan Python

Pastikan **Serial Monitor Arduino IDE ditutup** karena COM7 akan digunakan oleh Python.

Jalankan:

```bash
python read_hcsr04.py
```

Output yang diharapkan:

```text
====================================
ESP-12F + HC-SR04
JSON Serial Reader
====================================
Port    : COM7
Baudrate: 115200
Menunggu data...

Data Serial:
{"measurement":99,"duration":1606,"distance":27.54}

JSON VALID
Measurement : 99
Duration    : 1606 us
Distance    : 27.54 cm
Jarak hasil perhitungan Python : 27.54 cm
Selisih                        : 0.0029 cm
------------------------------------
```

---

# 11. Validasi JSON

Python menggunakan:

```python
data = json.loads(line)
```

Jika proses berhasil, berarti data yang diterima dapat diparsing sebagai JSON.

Contoh:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

akan menjadi Python dictionary:

```python
{
    "measurement": 99,
    "duration": 1606,
    "distance": 27.54
}
```

Tipe data:

```text
measurement → int
duration    → int
distance    → float
```

---

# 12. Validasi Konsistensi Data

Selain memvalidasi struktur JSON, program Python menghitung kembali jarak berdasarkan nilai `duration`.

Persamaan:

```python
calculated_distance = (duration * 0.0343) / 2
```

Kemudian dibandingkan dengan `distance` yang dikirim ESP-12F:

```python
difference = abs(
    distance - calculated_distance
)
```

Jika selisih sangat kecil, berarti nilai `distance` konsisten dengan `duration`.

### Contoh

Data:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

Perhitungan Python:

```text
Jarak ESP      = 27.54 cm
Jarak Python   = 27.54 cm
Selisih        ≈ 0.0029 cm
```

Hal tersebut menunjukkan bahwa **format JSON dan perhitungan internal ESP-12F konsisten**.

---

# 13. Validasi Akurasi Sensor

Validasi JSON tidak sama dengan validasi akurasi sensor.

Untuk menguji akurasi HC-SR04, diperlukan jarak referensi.

Contoh:

```text
Jarak referensi = 30.00 cm
Jarak sensor    = 27.54 cm
```

Absolute error:

$$
E = |d_{sensor}-d_{referensi}|
$$

$$
E = |27,54-30|
$$

$$
E = 2,46\text{ cm}
$$

Persentase error:

$$
E_{\%}
=
\frac{|d_{sensor}-d_{referensi}|}
{d_{referensi}}
\times100\%
$$

$$
E_{\%}
=
8,2\%
$$

Untuk penelitian, pengujian dapat dilakukan pada beberapa jarak referensi, misalnya:

```text
10 cm
20 cm
30 cm
40 cm
50 cm
60 cm
70 cm
80 cm
90 cm
100 cm
```

Kemudian data dapat digunakan untuk menghitung:

* Error absolut
* Error relatif
* Persentase error
* Mean Absolute Error (MAE)
* Root Mean Square Error (RMSE)
* Standar deviasi
* Presisi/repeatability
* Korelasi antara jarak referensi dan jarak sensor

---

# 14. Struktur Project

Struktur repository yang direkomendasikan:

```text
ESP12F-HCSR04-JSON/
│
├── README.md
│
├── arduino/
│   └── hcsr04_json.ino
│
├── python/
│   └── read_hcsr04.py
│
├── data/
│   └── data.json
│
└── docs/
    └── wiring.md
```

---

# 15. Alur Data

```text
HC-SR04
   │
   │ Echo pulse
   ▼
ESP-12F
   │
   │ Menghitung duration
   │
   ▼
distance = duration × 0.0343 / 2
   │
   ▼
JSON
   │
   │ Serial COM7
   ▼
Python
   │
   ├── json.loads()
   │
   ├── Validasi JSON
   │
   ├── Validasi duration-distance
   │
   └── Analisis data
```

---

# 16. Troubleshooting

### `UnicodeDecodeError`

Jika muncul:

```text
UnicodeDecodeError:
'utf-8' codec can't decode byte ...
```

gunakan:

```python
line = raw_data.decode(
    "utf-8",
    errors="ignore"
).strip()
```

ESP8266 dapat mengirim data startup/boot yang bukan UTF-8.

---

### `SerialException: could not open port COM7`

Kemungkinan COM7 sedang digunakan aplikasi lain.

Pastikan:

* Serial Monitor Arduino IDE ditutup.
* Tidak ada aplikasi serial lain yang menggunakan COM7.
* ESP-12F terhubung.
* COM port benar.

---

### Python tidak menerima data

Periksa:

```text
ESP-12F baudrate = 115200
Python baudrate  = 115200
```

dan pastikan:

```text
PORT = "COM7"
```

sesuai dengan COM port ESP-12F.

---

### JSON tidak valid

Pastikan output ESP hanya berupa:

```json
{"measurement":1,"duration":154,"distance":2.64}
```

dan tidak terdapat teks tambahan seperti:

```text
Jarak:
Distance:
Sensor:
```

karena Python mengharapkan satu JSON object pada setiap baris.

---

# 17. Pengembangan Berikutnya

Proyek ini dapat dikembangkan menjadi sistem akuisisi data lengkap:

```text
HC-SR04
    ↓
ESP-12F
    ↓
JSON
    ↓
Python
    ↓
┌───────────────┬───────────────┐
│               │               │
▼               ▼               ▼
JSON            CSV           Database
│               │
▼               ▼
Dataset       Excel
│
▼
Analisis / AI
```

Pengembangan yang direkomendasikan:

1. Penyimpanan otomatis ke `data.json`.
2. Penyimpanan ke CSV/Excel.
3. Akuisisi data dengan jumlah sampel tertentu.
4. Penambahan jarak referensi.
5. Perhitungan error otomatis.
6. Perhitungan MAE dan RMSE.
7. Visualisasi grafik jarak referensi vs jarak sensor.
8. Analisis repeatability.
9. Pengiriman data melalui Wi-Fi.
10. Integrasi dengan MQTT atau REST API.
11. Pengembangan dataset untuk aplikasi AI.

---

## 18. Status Proyek

**Current status:**

* [x] ESP-12F terdeteksi
* [x] ESP8266 Arduino Core terpasang
* [x] HC-SR04 dapat mengukur jarak
* [x] Data ditampilkan melalui Serial
* [x] Output menggunakan format JSON
* [x] Python dapat membaca data serial
* [x] JSON dapat divalidasi menggunakan `json.loads()`
* [x] Nilai `duration` dan `distance` dapat divalidasi secara matematis
* [ ] Penyimpanan otomatis ke `data.json`
* [ ] Pengujian akurasi terhadap jarak referensi
* [ ] Analisis MAE/RMSE
* [ ] Visualisasi data
* [ ] Integrasi dataset AI

---

## 19. Lisensi

Proyek ini dapat digunakan untuk keperluan pembelajaran, eksperimen, penelitian, dan pengembangan sistem instrumentasi dengan tetap mencantumkan sumber proyek apabila digunakan kembali.
