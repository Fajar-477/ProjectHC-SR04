# ESP-12F + HC-SR04 JSON Data Acquisition

Project ini menggunakan **ESP-12F (ESP8266)** dan **HC-SR04 ultrasonic sensor** untuk mengukur jarak. Data hasil pengukuran dikirim melalui komunikasi serial dalam format **JSON Lines (NDJSON)** dan kemudian dibaca serta diproses menggunakan **Python**.

Alur sistem:

```text
HC-SR04
   │
   │ Pengukuran jarak
   ▼
ESP-12F / ESP8266
   │
   │ Serial 115200 baud
   ▼
COM7
   │
   │ JSON Lines
   ▼
Python
   │
   ├── Membaca JSON
   ├── Validasi JSON
   ├── Mengambil measurement
   ├── Mengambil duration
   └── Mengambil distance
```

---

# 1. Fitur Project

Project ini memiliki beberapa fungsi utama:

* Mengukur jarak menggunakan HC-SR04.
* Menggunakan ESP-12F sebagai mikrokontroler.
* Mengirim data melalui serial.
* Menggunakan format JSON.
* Mengirim satu data JSON pada setiap baris.
* Membaca data secara real-time menggunakan Python.
* Memvalidasi struktur JSON.
* Memeriksa konsistensi nilai `duration` dan `distance`.
* Dapat dikembangkan untuk penyimpanan data, grafik, analisis statistik, atau machine learning.

---

# 2. Hardware yang Dibutuhkan

| No. | Komponen                    |     Jumlah |
| --: | --------------------------- | ---------: |
|   1 | ESP-12F / ESP8266           |          1 |
|   2 | HC-SR04                     |          1 |
|   3 | USB-to-TTL / USB programmer |          1 |
|   4 | Resistor 1 kΩ               |          1 |
|   5 | Resistor 2 kΩ               |          1 |
|   6 | Kabel jumper                | Secukupnya |
|   7 | Komputer/laptop             |          1 |

---

# 3. Koneksi HC-SR04 ke ESP-12F

Gunakan konfigurasi:

| HC-SR04 | ESP-12F                            |
| ------- | ---------------------------------- |
| VCC     | 5V                                 |
| GND     | GND                                |
| TRIG    | D1 / GPIO5                         |
| ECHO    | D2 / GPIO4 melalui voltage divider |

## 3.1 Voltage Divider ECHO

HC-SR04 umumnya menghasilkan sinyal ECHO sekitar 5 V, sedangkan GPIO ESP8266 menggunakan logika 3,3 V.

Karena itu, jangan menghubungkan ECHO HC-SR04 langsung ke GPIO ESP8266.

Gunakan rangkaian:

```text
HC-SR04 ECHO
      │
     1 kΩ
      │
      ├──────────────> D2 / GPIO4
      │
     2 kΩ
      │
     GND
```

Tegangan keluaran:

$$
V_{out}=V_{in}\frac{R_2}{R_1+R_2}
$$

Dengan:

$$
V_{in}=5V
$$

$$
R_1=1k\Omega
$$

$$
R_2=2k\Omega
$$

maka:

$$
V_{out}=5\frac{2}{1+2}
$$

$$
V_{out}\approx3,33V
$$

---

# 4. Persiapan Arduino IDE

## 4.1 Install Arduino IDE

Install Arduino IDE pada komputer.

Setelah instalasi selesai, buka Arduino IDE.

---

# 5. Install ESP8266 Board

ESP-12F menggunakan ESP8266 sehingga Arduino IDE harus memiliki package board ESP8266.

## 5.1 Buka Preferences

Pada Arduino IDE pilih:

```text
File
   ↓
Preferences
```

Cari:

```text
Additional Boards Manager URLs
```

Masukkan:

```text
https://arduino.esp8266.com/stable/package_esp8266com_index.json
```

Klik:

```text
OK
```

---

## 5.2 Install ESP8266

Kemudian pilih:

```text
Tools
   ↓
Board
   ↓
Boards Manager
```

Cari:

```text
ESP8266
```

Install:

```text
ESP8266 by ESP8266 Community
```

Setelah selesai, ESP8266 sudah dapat digunakan sebagai board Arduino IDE.

---

# 6. Hubungkan ESP-12F ke Komputer

Hubungkan ESP-12F melalui USB-to-TTL/programmer.

Setelah terhubung, buka:

```text
Tools → Port
```

Pada project ini port yang digunakan adalah:

```text
COM7
```

Jadi pilih:

```text
Tools → Port → COM7
```

Jika COM7 tidak muncul, periksa:

* Kabel USB.
* USB-to-TTL.
* Driver USB.
* Device Manager Windows.
* Apakah ESP-12F terdeteksi.

---

# 7. Pilih Board ESP-12F

Jangan memilih:

```text
Arduino Uno
Arduino Nano
Arduino Mega
```

Pilih:

```text
Tools
   ↓
Board
   ↓
ESP8266 Boards
   ↓
Generic ESP8266 Module
```

Untuk ESP-12F, konfigurasi `Generic ESP8266 Module` dapat digunakan.

---

# 8. Konfigurasi Board

Konfigurasi yang dapat digunakan:

```text
Board: Generic ESP8266 Module
Upload Speed: 115200
CPU Frequency: 80 MHz
Flash Size: 4MB
Port: COM7
```

Nama opsi dapat sedikit berbeda tergantung versi ESP8266 core dan Arduino IDE.

---

# 9. Buat Program Arduino

Pilih:

```text
File → New
```

Hapus kode yang ada kemudian masukkan program berikut.

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

  // Pastikan TRIG LOW
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  // Kirim pulsa trigger 10 mikrodetik
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Baca durasi pulsa ECHO
  duration = pulseIn(ECHO_PIN, HIGH, 30000);

  measurement++;

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

    // Jika ECHO tidak diterima
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

# 10. Simpan Program

Pilih:

```text
File → Save As
```

Gunakan nama:

```text
ESP12F_HCSR04_JSON
```

Sehingga file menjadi:

```text
ESP12F_HCSR04_JSON.ino
```

---

# 11. Verify / Compile Program

Sebelum upload, klik tombol:

```text
✓ Verify
```

Arduino IDE akan melakukan proses compile.

Jika berhasil, tidak akan muncul pesan error.

Pada ESP8266, output memory dapat terlihat seperti:

```text
Global variables use ...
IRAM ...
Flash ...
```

Informasi tersebut merupakan laporan penggunaan memory dan **bukan error**.

---

# 12. Upload Program ke ESP-12F

Setelah Verify berhasil, klik:

```text
→ Upload
```

Arduino IDE akan melakukan:

```text
Compile
   ↓
Connect to ESP8266
   ↓
Write firmware
   ↓
Verify
   ↓
Reset ESP8266
```

Jika berhasil, akan muncul informasi seperti:

```text
Chip is ESP8266EX
Features: WiFi
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Writing at ...
...
Hash of data verified.
Leaving...
Hard resetting via RTS pin...
```

Pesan:

```text
Hash of data verified.
```

menunjukkan bahwa data firmware berhasil diverifikasi.

---

# 13. Jika ESP-12F Tidak Bisa Upload

Jika muncul:

```text
Failed to connect
```

atau:

```text
Timed out waiting for packet header
```

ESP-12F mungkin belum masuk flash/programming mode.

Pada konfigurasi ESP-12F tertentu:

```text
GPIO0 → GND
```

kemudian reset ESP8266.

Setelah upload berhasil:

```text
GPIO0 → dilepas dari GND
```

kemudian reset kembali ESP8266.

Jika programmer memiliki tombol:

```text
FLASH
RST
```

gunakan tombol tersebut sesuai kebutuhan.

---

# 14. Buka Serial Monitor

Setelah upload berhasil, buka:

```text
Tools → Serial Monitor
```

Atur baud rate:

```text
115200
```

Hal ini harus sama dengan:

```cpp
Serial.begin(115200);
```

Jika baud rate salah, output dapat menjadi karakter acak.

---

# 15. Periksa Output Sensor

Jika semuanya berhasil, Serial Monitor akan menampilkan:

```json
{"measurement":1,"duration":1604,"distance":27.51}
{"measurement":2,"duration":1607,"distance":27.56}
{"measurement":3,"duration":1605,"distance":27.55}
{"measurement":4,"duration":1606,"distance":27.54}
```

Setiap baris adalah satu objek JSON.

Formatnya:

```text
{
    "measurement": nomor_pengukuran,
    "duration": durasi_echo,
    "distance": jarak
}
```

---

# 16. Penjelasan Parameter

Contoh:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

artinya:

| Parameter     | Nilai | Penjelasan           |
| ------------- | ----: | -------------------- |
| `measurement` |    99 | Pengukuran ke-99     |
| `duration`    |  1606 | Durasi ECHO dalam µs |
| `distance`    | 27.54 | Jarak dalam cm       |

---

# 17. Prinsip Perhitungan Jarak

HC-SR04 mengukur waktu perjalanan gelombang ultrasonik.

Rumus:

$$
d=\frac{t\times v}{2}
$$

Kode Arduino:

```cpp
distance = (duration * 0.0343) / 2.0;
```

Konstanta:

$$
v=0,0343\ cm/\mu s
$$

Faktor:

$$
\frac{1}{2}
$$

digunakan karena gelombang bergerak:

```text
Sensor → objek → sensor
```

Sehingga waktu yang diukur merupakan waktu pergi-pulang.

---

# 18. Pengujian Sensor

Letakkan objek pada jarak tertentu dari sensor.

Contohnya:

```text
HC-SR04
   │
   │
   │ 10 cm
   │
   ▼
  OBJEK
```

Kemudian lihat nilai:

```text
distance
```

Geser objek lebih jauh.

Nilai `distance` seharusnya meningkat.

Geser objek mendekati sensor.

Nilai `distance` seharusnya menurun.

---

# 19. Instalasi Python

Setelah bagian Arduino berhasil, tahap berikutnya adalah membaca data dari COM7 menggunakan Python.

Pastikan Python sudah terinstall.

Periksa dengan Command Prompt:

```bash
python --version
```

atau:

```bash
py --version
```

Contoh:

```text
Python 3.12.x
```

---

# 20. Install PySerial

Python membutuhkan library `pyserial` untuk berkomunikasi dengan COM7.

Buka Command Prompt:

```bash
pip install pyserial
```

Jika perintah tersebut tidak bekerja:

```bash
python -m pip install pyserial
```

Setelah selesai, periksa:

```bash
pip show pyserial
```

Jika berhasil, informasi package `pyserial` akan ditampilkan.

---

# 21. Sangat Penting: Tutup Serial Monitor

Sebelum menjalankan Python:

**TUTUP Arduino Serial Monitor.**

Alasannya adalah COM7 sedang digunakan oleh Arduino IDE.

Alurnya:

```text
Arduino Serial Monitor
        │
        └── menggunakan COM7
```

Jika Python juga mencoba menggunakan COM7:

```text
Python
   │
   └── COM7
```

maka dapat terjadi:

```text
PermissionError
Access is denied
```

atau:

```text
could not open port COM7
```

Jadi:

```text
Arduino Serial Monitor → TUTUP
```

kemudian:

```text
Python → buka COM7
```

---

# 22. Buat Program Python

Buat file baru:

```text
serial_reader.py
```

Masukkan:

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

    # Tunggu ESP8266 selesai reset
    time.sleep(2)

    # Buang data boot/reset yang mungkin tidak valid
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

        # Decode dengan aman
        line = raw_data.decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        # Hanya proses baris JSON
        if not line.startswith("{") or not line.endswith("}"):
            continue

        print("Data Serial:")
        print(line)

        try:

            # Parsing JSON
            data = json.loads(line)

            print("JSON VALID")

            measurement = data["measurement"]
            duration = data["duration"]
            distance = data["distance"]

            print("Measurement :", measurement)
            print("Duration    :", duration, "us")
            print("Distance    :", distance, "cm")

            # Validasi perhitungan
            if duration is not None and distance is not None:

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
                    "Selisih :",
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

# 23. Menjalankan Python

Buka Command Prompt pada folder tempat:

```text
serial_reader.py
```

berada.

Contoh:

```bash
cd C:\nama_folder_project
```

Kemudian:

```bash
python serial_reader.py
```

Jika menggunakan launcher Python:

```bash
py serial_reader.py
```

---

# 24. Output Python

Jika berhasil, program akan menampilkan:

```text
====================================
ESP-12F + HC-SR04
JSON Serial Reader
====================================
Port    : COM7
Baudrate: 115200
Menunggu data...
```

Kemudian:

```text
Data Serial:
{"measurement":99,"duration":1606,"distance":27.54}

JSON VALID
Measurement : 99
Duration    : 1606 us
Distance    : 27.54 cm
Jarak hasil perhitungan Python : 27.54 cm
Selisih : 0.0029 cm
------------------------------------
```

Dengan demikian, data telah berhasil berpindah:

```text
HC-SR04
    ↓
ESP-12F
    ↓
Serial
    ↓
COM7
    ↓
JSON
    ↓
Python
    ↓
Python Dictionary
```

---

# 25. Bagaimana Python Membaca JSON?

Data dari ESP8266 awalnya berupa teks:

```text
{"measurement":99,"duration":1606,"distance":27.54}
```

Python menerima data tersebut sebagai `bytes`.

Contohnya:

```python
raw_data = ser.readline()
```

Kemudian diubah menjadi string:

```python
line = raw_data.decode(
    "utf-8",
    errors="ignore"
).strip()
```

Kemudian JSON diubah menjadi Python dictionary:

```python
data = json.loads(line)
```

Sehingga:

```python
data
```

menjadi:

```python
{
    "measurement": 99,
    "duration": 1606,
    "distance": 27.54
}
```

Kemudian masing-masing nilai dapat diambil:

```python
measurement = data["measurement"]

duration = data["duration"]

distance = data["distance"]
```

---

# 26. Validasi JSON

Python menggunakan:

```python
json.loads(line)
```

Jika JSON benar:

```text
JSON VALID
```

Jika JSON rusak:

```text
JSON TIDAK VALID
```

Contoh JSON valid:

```json
{"measurement":1,"duration":1606,"distance":27.54}
```

Contoh tidak valid:

```text
{"measurement":1,"duration":1606,"distance":27.54
```

karena tanda:

```text
}
```

hilang.

---

# 27. Validasi Perhitungan Jarak

Data Arduino:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

Python menghitung ulang:

```python
calculated_distance = (
    duration * 0.0343
) / 2
```

Hasil:

$$
d=\frac{1606\times0,0343}{2}
$$

$$
d\approx27,54\ cm
$$

Kemudian Python membandingkan:

```python
difference = abs(
    distance - calculated_distance
)
```

Jika selisih sangat kecil, berarti nilai `distance` yang dikirim Arduino konsisten dengan `duration`.

---

# 28. Perbedaan Validasi JSON dan Akurasi Sensor

Hal ini penting dalam analisis project.

### Validasi JSON

Menjawab:

> Apakah data yang dikirim ESP8266 memiliki format JSON yang benar?

Contoh:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

### Validasi matematis

Menjawab:

> Apakah `distance` sesuai dengan `duration` berdasarkan rumus program?

### Validasi sensor

Menjawab:

> Apakah jarak yang diukur sensor benar secara fisik?

Validasi sensor membutuhkan pembanding.

Contohnya:

```text
Jarak sebenarnya = 30 cm
Jarak sensor      = 29,5 cm
```

Error:

$$
Error=|30-29,5|
$$

$$
Error=0,5\ cm
$$

Persentase error:

$$
Error(\%)=
\frac{|d_{actual}-d_{sensor}|}
{d_{actual}}
\times100\%
$$

---

# 29. Jika Python Mendapat UnicodeDecodeError

Jika muncul:

```text
UnicodeDecodeError
```

gunakan:

```python
line = raw_data.decode(
    "utf-8",
    errors="ignore"
).strip()
```

Jangan menggunakan:

```python
line = raw_data.decode("utf-8").strip()
```

secara langsung jika ESP8266 mengeluarkan byte boot/reset yang bukan UTF-8.

Kode project ini sudah menggunakan:

```python
errors="ignore"
```

untuk menghindari masalah tersebut.

---

# 30. Jika Python Tidak Bisa Membuka COM7

Jika muncul:

```text
PermissionError
```

atau:

```text
could not open port COM7
```

periksa:

1. Serial Monitor Arduino IDE sudah ditutup.
2. Tidak ada program lain yang menggunakan COM7.
3. ESP-12F masih terhubung.
4. Port masih COM7.
5. Tidak ada Python script lain yang sedang menggunakan COM7.

Periksa kembali:

```text
Device Manager
   ↓
Ports (COM & LPT)
```

---

# 31. Jika Python Tidak Mendapatkan Data

Jika program menampilkan:

```text
Menunggu data...
```

tetapi tidak ada data, periksa:

### Baudrate

Arduino:

```cpp
Serial.begin(115200);
```

Python:

```python
BAUDRATE = 115200
```

Keduanya harus sama.

### Port

Arduino menggunakan:

```text
COM7
```

Python:

```python
PORT = "COM7"
```

### Serial Monitor

Pastikan Serial Monitor sudah ditutup.

### ESP8266

Pastikan program sudah berhasil di-upload.

---

# 32. Jika Output Arduino Berupa Karakter Acak

Contoh:

```text
���⸮�⸮
```

Kemungkinan baudrate tidak sesuai.

Atur Serial Monitor ke:

```text
115200
```

dan pastikan program:

```cpp
Serial.begin(115200);
```

---

# 33. Jika Output JSON Tidak Muncul

Periksa koneksi:

```text
HC-SR04 VCC → 5V
HC-SR04 GND → GND
HC-SR04 TRIG → D1
HC-SR04 ECHO → voltage divider → D2
```

Kemudian periksa apakah program berhasil upload.

---

# 34. Jika `distance` Bernilai `null`

Contoh:

```json
{"measurement":20,"duration":null,"distance":null}
```

Artinya:

```cpp
pulseIn()
```

tidak mendapatkan pulsa ECHO dalam batas waktu 30.000 µs.

Periksa:

* VCC HC-SR04.
* GND.
* TRIG.
* ECHO.
* Voltage divider.
* Posisi objek.
* Jarak objek.

---

# 35. Menghentikan Program Python

Tekan:

```text
CTRL + C
```

Python kemudian menjalankan:

```python
ser.close()
```

sehingga COM7 dilepaskan.

Output:

```text
Program dihentikan.
Serial port ditutup.
```

---

# 36. Struktur Folder Project

Struktur sederhana:

```text
ESP12F-HCSR04-JSON/
│
├── Arduino/
│   └── ESP12F_HCSR04_JSON/
│       └── ESP12F_HCSR04_JSON.ino
│
├── Python/
│   └── serial_reader.py
│
└── README.md
```

Jika nantinya data ingin disimpan:

```text
ESP12F-HCSR04-JSON/
│
├── Arduino/
│   └── ESP12F_HCSR04_JSON/
│       └── ESP12F_HCSR04_JSON.ino
│
├── Python/
│   ├── serial_reader.py
│   ├── data.csv
│   └── analysis.py
│
└── README.md
```

---

# 37. Alur Lengkap Menjalankan Project

Urutan yang direkomendasikan adalah:

```text
1. Hubungkan HC-SR04
        ↓
2. Hubungkan ESP-12F
        ↓
3. Buka Arduino IDE
        ↓
4. Pastikan ESP8266 core terinstall
        ↓
5. Pilih Generic ESP8266 Module
        ↓
6. Pilih COM7
        ↓
7. Masukkan kode Arduino
        ↓
8. Verify
        ↓
9. Upload
        ↓
10. Buka Serial Monitor
        ↓
11. Atur 115200 baud
        ↓
12. Pastikan JSON muncul
        ↓
13. Tutup Serial Monitor
        ↓
14. Buka Command Prompt
        ↓
15. Jalankan Python
        ↓
16. Python membuka COM7
        ↓
17. Python membaca JSON
        ↓
18. json.loads()
        ↓
19. Data menjadi Python dictionary
        ↓
20. Validasi duration-distance
```

---

# 38. Checklist Final

Sebelum menyatakan project berhasil, pastikan:

```text
HARDWARE
[✓] ESP-12F terhubung
[✓] HC-SR04 terhubung
[✓] VCC = 5V
[✓] GND terhubung
[✓] TRIG = D1 / GPIO5
[✓] ECHO = D2 / GPIO4
[✓] Voltage divider ECHO digunakan

ARDUINO IDE
[✓] ESP8266 core terinstall
[✓] Board = Generic ESP8266 Module
[✓] Port = COM7
[✓] Verify berhasil
[✓] Upload berhasil
[✓] Serial Monitor = 115200
[✓] JSON muncul

PYTHON
[✓] Python terinstall
[✓] PySerial terinstall
[✓] Serial Monitor ditutup
[✓] Python menggunakan COM7
[✓] Python menggunakan 115200 baud
[✓] JSON berhasil dibaca
[✓] JSON berhasil di-parse
[✓] measurement berhasil dibaca
[✓] duration berhasil dibaca
[✓] distance berhasil dibaca
[✓] Perhitungan distance dapat divalidasi
```

---

# 39. Contoh Hasil Akhir

### Output ESP-12F

```json
{"measurement":1,"duration":1163,"distance":19.94}
{"measurement":2,"duration":1165,"distance":19.99}
{"measurement":3,"duration":1161,"distance":19.91}
```

### Output Python

```text
Data Serial:
{"measurement":1,"duration":1163,"distance":19.94}

JSON VALID
Measurement : 1
Duration    : 1163 us
Distance    : 19.94 cm
Jarak hasil perhitungan Python : 19.94 cm
Selisih : 0.00005 cm
------------------------------------
```

Hal ini menunjukkan bahwa:

```text
HC-SR04
   ↓
ESP-12F
   ↓
Pengukuran duration
   ↓
Perhitungan distance
   ↓
JSON
   ↓
Serial COM7
   ↓
Python
   ↓
json.loads()
   ↓
Python Dictionary
```

telah berjalan dengan benar.

---

# 40. Pengembangan Selanjutnya

Project ini dapat dikembangkan lebih lanjut menjadi sistem akuisisi data yang lebih lengkap, misalnya:

* Menyimpan data ke CSV.
* Menyimpan data ke Excel.
* Membuat grafik jarak terhadap waktu.
* Menghitung rata-rata pengukuran.
* Menghitung standar deviasi.
* Menghitung error pengukuran.
* Membandingkan sensor dengan jarak referensi.
* Membuat dashboard Python.
* Mengirim data melalui Wi-Fi.
* Menggunakan MQTT.
* Mengirim data ke database.
* Melakukan filtering data sensor.
* Membangun sistem monitoring real-time.

---

# 41. Ringkasan

Project menggunakan ESP-12F dan HC-SR04 untuk memperoleh data jarak. ESP8266 membaca durasi pulsa ECHO dan menghitung jarak menggunakan:

$$
d=\frac{t\times0,0343}{2}
$$

Data kemudian dikirim melalui serial COM7 dengan baudrate 115200 dalam format JSON Lines:

```json
{"measurement":99,"duration":1606,"distance":27.54}
```

Python menggunakan `pyserial` untuk membaca COM7 dan `json.loads()` untuk mengubah data JSON menjadi Python dictionary.

Dengan demikian, sistem memiliki alur:

```text
        HC-SR04
           │
           ▼
      ESP-12F
           │
           ▼
   Serial 115200 baud
           │
           ▼
         COM7
           │
           ▼
      JSON / NDJSON
           │
           ▼
        Python
           │
           ├── JSON parsing
           ├── Data extraction
           ├── Validation
           └── Data analysis
```

Project ini dapat digunakan sebagai dasar untuk membangun sistem **data acquisition dan analisis sensor berbasis ESP8266 + Python**.
