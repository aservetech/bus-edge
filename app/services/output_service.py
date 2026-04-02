# =========================
# GPIO BACKEND SELECTION
# =========================
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()


# =========================
# IMPORTS
# =========================
import json
from pathlib import Path
from gpiozero import OutputDevice


# =========================
# OUTPUT SERVICE
# =========================
class OutputService:
    def __init__(self, file_path="data/output_status.json", relay_pin=17):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # -------------------------
        # RELAY CONFIGURATION
        # active_high=True means:
        #   on()  -> GPIO goes HIGH -> relay ON
        #   off() -> GPIO goes LOW  -> relay OFF
        # -------------------------
        self.relay = OutputDevice(
            relay_pin,
            active_high=True,
            initial_value=False,
        )

        if not self.file_path.exists():
            self._save_status(active=False, message="Output OFF")
        else:
            self.off()

    # =========================
    # INTERNAL HELPERS
    # =========================
    def _save_status(self, active: bool, message: str):
        data = {
            "active": active,
            "message": message,
        }
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    # =========================
    # PUBLIC METHODS
    # =========================
    def on(self):
        print("🔊 OUTPUT ON")
        self.relay.on()
        self._save_status(active=True, message="Output ON")

    def off(self):
        print("🔇 OUTPUT OFF")
        self.relay.off()
        self._save_status(active=False, message="Output OFF")

    def get_status(self):
        with open(self.file_path, "r") as f:
            return json.load(f)
