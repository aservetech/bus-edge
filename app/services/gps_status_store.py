# =========================
# IMPORTS
# =========================
import json
from pathlib import Path


# =========================
# GPS STATUS STORE
# =========================
class GPSStatusStore:
    def __init__(self, file_path="data/gps_status.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self.set_status(
                active=False,
                message="Waiting for GPS fix",
                lat=None,
                lon=None,
            )

    # =========================
    # WRITE STATUS
    # =========================
    def set_status(self, active: bool, message: str, lat=None, lon=None):
        data = {
            "active": active,
            "message": message,
            "lat": lat,
            "lon": lon,
        }
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    # =========================
    # READ STATUS
    # =========================
    def get_status(self):
        with open(self.file_path, "r") as f:
            return json.load(f)
