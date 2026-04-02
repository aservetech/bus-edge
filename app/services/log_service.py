# =========================
# IMPORTS
# =========================
import csv
from pathlib import Path
from datetime import datetime


# =========================
# LOG SERVICE
# =========================
class LogService:
    def __init__(self, file_path="data/geofence_log.csv"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            with open(self.file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "latitude",
                    "longitude",
                    "geofence_name",
                    "distance_meters",
                    "inside",
                    "event",
                    "alert_active",
                    "output_active",
                ])

    # =========================
    # WRITE LOG ENTRY
    # =========================
    def log_event(
        self,
        latitude,
        longitude,
        geofence_name,
        distance_meters,
        inside,
        event,
        alert_active,
        output_active,
    ):
        with open(self.file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                latitude,
                longitude,
                geofence_name,
                round(distance_meters, 2) if distance_meters is not None else None,
                inside,
                event,
                alert_active,
                output_active,
            ])
