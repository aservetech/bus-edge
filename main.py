# =========================
# IMPORTS
# =========================
import time
from app.services.geofence_service import GeofenceService
from app.services.gps_service import GPSService
from app.services.geofence_store import GeofenceStore
from app.services.alert_store import AlertStore
from app.services.output_service import OutputService
from app.services.gps_status_store import GPSStatusStore
from app.services.log_service import LogService


# =========================
# SERVICES INITIALIZATION
# =========================
gps_service = GPSService()
store = GeofenceStore()
alert_store = AlertStore()
output_service = OutputService()
gps_status_store = GPSStatusStore()
log_service = LogService()

active_states = {}
last_output_state = None


# =========================
# CLEAR STALE STATE ON STARTUP
# =========================
alert_store.set_status(False, "No active alerts")
gps_status_store.set_status(False, "Initializing GPS...", None, None)
output_service.off()


# =========================
# GEOFENCE CHECK LOGIC
# =========================
def check_all_geofences(lat, lon):
    global last_output_state

    geofences = store.get_all()
    any_active = False
    active_message = "No active alerts"

    for g in geofences:
        key = g["name"]

        geofence = GeofenceService(
            geofence_lat=g["lat"],
            geofence_lon=g["lon"],
            radius_meters=g["radius"],
        )

        result = geofence.check_position(lat, lon)

        prev_inside = active_states.get(key, False)
        current_inside = result["inside"]
        distance_meters = result["distance"]

        print(
            f"Distance to {g['name']}: {distance_meters:.2f} meters | Inside: {current_inside}"
        )

        # =========================
        # ACTIVE ALERT MESSAGE
        # =========================
        if current_inside:
            any_active = True
            note = g.get("note", "").strip()
            active_message = f"LOW BRIDGE: {g['name']}"
            if note:
                active_message += f" ({note})"

        # =========================
        # LOG CHECK EVENT
        # =========================
        log_service.log_event(
            latitude=lat,
            longitude=lon,
            geofence_name=g["name"],
            distance_meters=distance_meters,
            inside=current_inside,
            event="CHECK",
            alert_active=any_active,
            output_active=(last_output_state is True),
        )

        # =========================
        # ENTER EVENT
        # =========================
        if current_inside and not prev_inside:
            note = g.get("note", "").strip()
            print(f"🚨 ENTERED: {g['name']}" + (f" ({note})" if note else ""))

            log_service.log_event(
                latitude=lat,
                longitude=lon,
                geofence_name=g["name"],
                distance_meters=distance_meters,
                inside=True,
                event="ENTER",
                alert_active=True,
                output_active=True,
            )

        # =========================
        # EXIT EVENT
        # =========================
        elif not current_inside and prev_inside:
            print(f"✅ EXITED: {g['name']}")

            log_service.log_event(
                latitude=lat,
                longitude=lon,
                geofence_name=g["name"],
                distance_meters=distance_meters,
                inside=False,
                event="EXIT",
                alert_active=False,
                output_active=False,
            )

        active_states[key] = current_inside

    # =========================
    # DASHBOARD ALERT STATUS
    # =========================
    alert_store.set_status(active=any_active, message=active_message)

    # =========================
    # OUTPUT STATE CONTROL
    # only change when state changes
    # =========================
    if any_active != last_output_state:
        if any_active:
            output_service.on()
        else:
            output_service.off()

        last_output_state = any_active


# =========================
# MAIN LOOP
# =========================
print("🚀 Bus Edge System Started (REAL GPS MODE)")

while True:
    lat, lon = gps_service.get_position()

    if lat is None or lon is None:
        print("Waiting for GPS fix...")

        gps_status_store.set_status(
            active=False,
            message="Waiting for GPS fix",
            lat=None,
            lon=None,
        )

        alert_store.set_status(
            active=False,
            message="Waiting for GPS fix",
        )

        if last_output_state is not False:
            output_service.off()
            last_output_state = False

        time.sleep(1)
        continue

    print(f"GPS: {lat}, {lon}")

    gps_status_store.set_status(
        active=True,
        message="GPS Active",
        lat=lat,
        lon=lon,
    )

    check_all_geofences(lat, lon)

    time.sleep(1)
