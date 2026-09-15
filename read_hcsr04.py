
import serial
import json
import time

# ==========================================
# Konfigurasi Serial
# ==========================================

PORT = "COM7"
BAUDRATE = 115200

# ==========================================
# Membuka Serial Port
# ==========================================

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        timeout=1
    )

    # Tunggu ESP8266 selesai reset
    time.sleep(2)

    # Bersihkan data awal yang ada di buffer
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

        # ==========================================
        # Membaca satu baris dari ESP8266
        # ==========================================

        raw_data = ser.readline()

        if not raw_data:
            continue

        # Decode dengan mengabaikan byte yang tidak valid
        line = raw_data.decode(
            "utf-8",
            errors="ignore"
        ).strip()

        # Jika baris kosong
        if not line:
            continue

        # ==========================================
        # Memastikan data terlihat seperti JSON
        # ==========================================

        if not line.startswith("{") or not line.endswith("}"):
            continue

        print("Data Serial:")
        print(line)

        # ==========================================
        # Membaca JSON
        # ==========================================

        try:

            data = json.loads(line)

            print("JSON VALID")

            # Mengambil nilai JSON
            measurement = data["measurement"]
            duration = data["duration"]
            distance = data["distance"]

            print("Measurement :", measurement)
            print("Duration    :", duration, "us")
            print("Distance    :", distance, "cm")

            # ======================================
            # Validasi perhitungan jarak
            # ======================================

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

    print("\nProgram dihentikan oleh pengguna.")

finally:

    ser.close()

    print("Serial port ditutup.")
