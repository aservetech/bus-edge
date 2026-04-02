# =========================
# IMPORTS
# =========================
import serial
import time


# =========================
# GPS CONFIG
# =========================
GPS_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600


# =========================
# PARSE NMEA LAT/LON
# =========================
def convert_to_decimal(degrees, direction):
    if not degrees:
        return None

    d = float(degrees[:2])
    m = float(degrees[2:])

    result = d + (m / 60)

    if direction in ["S", "W"]:
        result *= -1

    return result


# =========================
# GET GPS DATA
# =========================
def get_gps_data():
    try:
        with serial.Serial(GPS_PORT, BAUD_RATE, timeout=1) as ser:
            start_time = time.time()

            while time.time() - start_time < 2:
                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if "$GPGGA" in line:
                    parts = line.split(",")

                    if len(parts) > 5 and parts[2] and parts[4]:
                        lat = convert_to_decimal(parts[2], parts[3])
                        lon = convert_to_decimal(parts[4], parts[5])

                        if lat and lon:
                            return {
                                "lat": lat,
                                "lon": lon,
                            }

        return None

    except Exception as e:
        print(f"GPS ERROR: {e}")
        return None
