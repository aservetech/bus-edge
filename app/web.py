# =========================
# IMPORTS
# =========================
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.geofence_store import GeofenceStore
from app.services.alert_store import AlertStore
from app.services.gps_status_store import GPSStatusStore


# =========================
# APP SETUP
# =========================
app = FastAPI()

PROJECT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_DIR / "templates"
DATA_DIR = PROJECT_DIR / "data"
GEOFENCE_FILE = DATA_DIR / "geofences.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# =========================
# SERVICES
# =========================
store = GeofenceStore(file_path=str(GEOFENCE_FILE))
alert_store = AlertStore(file_path=str(DATA_DIR / "alert_status.json"))
gps_status_store = GPSStatusStore(file_path=str(DATA_DIR / "gps_status.json"))


# =========================
# OUTPUT STATUS READER
# =========================
OUTPUT_STATUS_FILE = DATA_DIR / "output_status.json"


def get_output_status():
    if not OUTPUT_STATUS_FILE.exists():
        return {
            "active": False,
            "message": "Output OFF",
        }

    with open(OUTPUT_STATUS_FILE, "r") as f:
        return json.load(f)


# =========================
# DASHBOARD
# =========================
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    geofences = store.get_all()
    alert_status = alert_store.get_status()
    output_status = get_output_status()
    gps_status = gps_status_store.get_status()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "geofences": geofences,
            "device_name": "ai-bot",
            "gps_status": gps_status["message"],
            "gps_lat": gps_status["lat"],
            "gps_lon": gps_status["lon"],
            "last_event": "Monitoring geofences",
            "alert_active": alert_status["active"],
            "alert_message": alert_status["message"],
            "output_active": output_status["active"],
            "output_message": output_status["message"],
        },
    )


# =========================
# ADD GEOFENCE
# =========================
@app.post("/add-geofence")
async def add_geofence(request: Request):
    form = await request.form()

    geofence = {
        "name": form.get("name", "").strip(),
        "lat": float(form.get("lat")),
        "lon": float(form.get("lon")),
        "radius": int(form.get("radius")),
        "note": form.get("note", "").strip(),
    }

    store.add(geofence)
    return RedirectResponse(url="/", status_code=303)


# =========================
# DELETE GEOFENCE
# =========================
@app.post("/delete-geofence")
async def delete_geofence(request: Request):
    form = await request.form()
    name = form.get("name", "").strip()

    geofences = store.get_all()
    updated_geofences = [g for g in geofences if g.get("name", "").strip() != name]

    with open(GEOFENCE_FILE, "w") as f:
        json.dump(updated_geofences, f, indent=2)

    return RedirectResponse(url="/", status_code=303)


# =========================
# LIVE ALERT ENDPOINT
# =========================
@app.get("/alert-status")
def alert_status_endpoint():
    return alert_store.get_status()


# =========================
# LIVE OUTPUT ENDPOINT
# =========================
@app.get("/output-status")
def output_status_endpoint():
    return get_output_status()


# =========================
# LIVE GPS STATUS ENDPOINT
# =========================
@app.get("/gps-status")
def gps_status_endpoint():
    return gps_status_store.get_status()
