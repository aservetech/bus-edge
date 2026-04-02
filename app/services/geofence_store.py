import json
from pathlib import Path


class GeofenceStore:
    def __init__(self, file_path="data/geofences.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self._save([])

    def _load(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_all(self):
        return self._load()

    def add(self, geofence):
        data = self._load()
        data.append(geofence)
        self._save(data)
