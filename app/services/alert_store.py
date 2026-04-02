import json
from pathlib import Path


class AlertStore:
    def __init__(self, file_path="data/alert_status.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self.set_status(active=False, message="No active alerts")

    def set_status(self, active: bool, message: str):
        data = {
            "active": active,
            "message": message,
        }
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_status(self):
        with open(self.file_path, "r") as f:
            return json.load(f)
