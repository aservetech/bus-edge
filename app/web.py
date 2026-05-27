import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.geofence_store import GeofenceStore
from app.services.alert_store import AlertStore
from app.services.gps_status_store import GPSStatusStore


app = FastAPI()

PROJECT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PROJECT_DIR / "templates"
DATA_DIR = PROJECT_DIR / "data"
GEOFENCE_FILE = DATA_DIR / "geofences.json"
OUTPUT_STATUS_FILE = DATA_DIR / "output_status.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

store = GeofenceStore(file_path=str(GEOFENCE_FILE))
alert_store = AlertStore(file_path=str(DATA_DIR / "alert_status.json"))
gps_status_store = GPSStatusStore(file_path=str(DATA_DIR / "gps_status.json"))


def get_output_status():
    if not OUTPUT_STATUS_FILE.exists():
        return {
            "active": False,
            "message": "Output OFF",
        }

    with open(OUTPUT_STATUS_FILE, "r") as f:
        return json.load(f)


def save_geofences(geofences):
    with open(GEOFENCE_FILE, "w") as f:
        json.dump(geofences, f, indent=2)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    geofences = store.get_all()
    alert_status = alert_store.get_status()
    output_status = get_output_status()
    gps_status = gps_status_store.get_status()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "geofences": geofences,
            "device_name": "ai-bot",
            "gps_status": gps_status.get("message", "Waiting for GPS fix"),
            "gps_lat": gps_status.get("lat"),
            "gps_lon": gps_status.get("lon"),
            "last_event": "Monitoring geofences",
            "alert_active": alert_status.get("active", False),
            "alert_message": alert_status.get("message", "No active alerts"),
            "output_active": output_status.get("active", False),
            "output_message": output_status.get("message", "Output OFF"),
        },
    )


@app.post("/add-geofence")
async def add_geofence(request: Request):
    form = await request.form()

    try:
        geofence = {
            "name": form.get("name", "").strip(),
            "lat": float(form.get("lat")),
            "lon": float(form.get("lon")),
            "radius": int(float(form.get("radius"))),
            "note": form.get("note", "").strip(),
        }
    except ValueError:
        return HTMLResponse(
            "Invalid geofence. Latitude, longitude, and radius must be numbers.",
            status_code=400,
        )

    store.add(geofence)
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete-geofence")
async def delete_geofence(request: Request):
    form = await request.form()
    name = form.get("name", "").strip()

    geofences = store.get_all()
    updated_geofences = [
        g for g in geofences
        if g.get("name", "").strip() != name
    ]

    save_geofences(updated_geofences)

    return RedirectResponse(url="/", status_code=303)


@app.post("/edit-geofence")
async def edit_geofence(request: Request):
    form = await request.form()
    original_name = form.get("original_name", "").strip()

    try:
        updated_geofence = {
            "name": form.get("name", "").strip(),
            "lat": float(form.get("lat")),
            "lon": float(form.get("lon")),
            "radius": int(float(form.get("radius"))),
            "note": form.get("note", "").strip(),
        }
    except ValueError:
        return HTMLResponse(
            "Invalid geofence. Latitude, longitude, and radius must be numbers.",
            status_code=400,
        )

    geofences = store.get_all()

    for i, g in enumerate(geofences):
        if g.get("name", "").strip() == original_name:
            geofences[i] = updated_geofence
            break

    save_geofences(geofences)

    return RedirectResponse(url="/", status_code=303)


@app.get("/alert-status")
def alert_status_endpoint():
    return alert_store.get_status()


@app.get("/output-status")
def output_status_endpoint():
    return get_output_status()


@app.get("/gps-status")
def gps_status_endpoint():
    return gps_status_store.get_status()
