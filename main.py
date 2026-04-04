# =========================
# IMPORTS
# =========================
import json
import math
import time
from pathlib import Path

import gpsd
from gpiozero import OutputDevice
from gpiozero.pins.lgpio import LGPIOFactory


# =========================
# PATHS
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

GEOFENCE_FILE = DATA_DIR / "geofences.json"
GPS_STATUS_FILE = DATA_DIR / "gps_status.json"
ALERT_STATUS_FILE = DATA_DIR / "alert_status.json"
OUTPUT_STATUS_FILE = DATA_DIR / "output_status.json"
LOG_FILE = DATA_DIR / "geofence_log.csv"


# =========================
# CONFIG
# =========================
RELAY_GPIO = 17     # BCM 17 = physical pin 11
LOOP_DELAY = 1


# =========================
# RELAY SETUP
# =========================
PIN_FACTORY = LGPIOFactory()

relay = OutputDevice(
    RELAY_GPIO,
    active_high=False,   # active LOW relay
    initial_value=False, # OFF at startup
    pin_factory=PIN_FACTORY
)


# =========================
# HELPERS
# =========================
def write_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def init_status_files() -> None:
    if not GPS_STATUS_FILE.exists():
        write_json(GPS_STATUS_FILE, {
            "lat": 0,
            "lon": 0,
            "message": "Waiting for GPS fix"
        })

    if not ALERT_STATUS_FILE.exists():
        write_json(ALERT_STATUS_FILE, {
            "active": False,
            "message": "System monitoring geofences"
        })

    if not OUTPUT_STATUS_FILE.exists():
        write_json(OUTPUT_STATUS_FILE, {
            "active": False,
            "message": "Output OFF"
        })

    if not LOG_FILE.exists():
        with open(LOG_FILE, "w") as f:
            f.write("timestamp,event,name,lat,lon,distance_m,radius_m,note\n")


def update_gps_status(lat: float, lon: float, has_fix: bool) -> None:
    message = "GPS FIX ACQUIRED" if has_fix else "Waiting for GPS fix"
    write_json(GPS_STATUS_FILE, {
        "lat": lat,
        "lon": lon,
        "message": message
    })


def update_alert_status(active: bool, message: str) -> None:
    write_json(ALERT_STATUS_FILE, {
        "active": active,
        "message": message
    })


def update_output_status(active: bool) -> None:
    write_json(OUTPUT_STATUS_FILE, {
        "active": active,
        "message": "Output ON" if active else "Output OFF"
    })


def load_geofences():
    if not GEOFENCE_FILE.exists():
        return []

    try:
        with open(GEOFENCE_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Failed to load geofences: {e}")
        return []


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000  # meters
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def output_on():
    relay.on()
    update_output_status(True)
    print("🔔 OUTPUT ON")


def output_off():
    relay.off()
    update_output_status(False)
    print("🔇 OUTPUT OFF")


def log_event(event, name, lat, lon, distance_m, radius_m, note):
    safe_note = (note or "").replace(",", ";")
    with open(LOG_FILE, "a") as f:
        f.write(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')},"
            f"{event},{name},{lat},{lon},{distance_m:.2f},{radius_m},{safe_note}\n"
        )


# =========================
# GPS
# =========================
def init_gps():
    gpsd.connect()
    print("GPSD connected")


def get_packet():
    try:
        return gpsd.get_current()
    except Exception as e:
        print(f"GPS read error: {e}")
        return None


# =========================
# MAIN
# =========================
def main():
    print("🚀 Bus Edge System Started (REAL GPS MODE)")
    init_status_files()
    init_gps()

    inside_geofences = set()
    output_is_on = False

    output_off()
    update_alert_status(False, "System monitoring geofences")

    while True:
        packet = get_packet()

        if packet is None:
            update_gps_status(0, 0, False)
            update_alert_status(False, "System monitoring geofences")
            if output_is_on:
                output_off()
                output_is_on = False
            print("Waiting for GPS fix...")
            time.sleep(LOOP_DELAY)
            continue

        lat = getattr(packet, "lat", 0) or 0
        lon = getattr(packet, "lon", 0) or 0
        mode = getattr(packet, "mode", 0) or 0

        has_fix = mode >= 2 and lat != 0 and lon != 0
        update_gps_status(lat, lon, has_fix)

        if not has_fix:
            update_alert_status(False, "System monitoring geofences")
            if output_is_on:
                output_off()
                output_is_on = False
            print("Waiting for GPS fix...")
            time.sleep(LOOP_DELAY)
            continue

        print(f"📍 Lat: {lat} | Lon: {lon} | Mode: {mode}")

        geofences = load_geofences()
        currently_inside = set()
        nearest_inside = None

        for g in geofences:
            try:
                name = g.get("name", "Unnamed")
                gf_lat = float(g["lat"])
                gf_lon = float(g["lon"])
                radius = float(g["radius"])
                note = g.get("note", "")

                distance = haversine_m(lat, lon, gf_lat, gf_lon)
                print(f"➡️ {name}: {distance:.2f}m away (radius {radius}m)")

                if distance <= radius:
                    currently_inside.add(name)

                    if nearest_inside is None or distance < nearest_inside["distance"]:
                        nearest_inside = {
                            "name": name,
                            "distance": distance,
                            "radius": radius,
                            "note": note,
                        }

                    if name not in inside_geofences:
                        print(f"🚨 ENTERED GEOFENCE: {name}")
                        log_event("ENTER", name, lat, lon, distance, radius, note)

            except Exception as e:
                print(f"Error processing geofence {g}: {e}")

        # Handle exits
        exited_geofences = inside_geofences - currently_inside
        for exited_name in exited_geofences:
            print(f"✅ EXITED GEOFENCE: {exited_name}")
            log_event("EXIT", exited_name, lat, lon, 0, 0, "")

        inside_geofences = currently_inside

        # Output and alert behavior
        if inside_geofences:
            active_names = ", ".join(sorted(inside_geofences))
            update_alert_status(True, f"Inside geofence: {active_names}")

            if not output_is_on:
                output_on()
                output_is_on = True
        else:
            update_alert_status(False, "System monitoring geofences")

            if output_is_on:
                output_off()
                output_is_on = False

        time.sleep(LOOP_DELAY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        output_off()
        relay.close()
