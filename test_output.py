# =========================
# GPIO BACKEND
# =========================
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

Device.pin_factory = LGPIOFactory()

# =========================
# IMPORTS
# =========================
from gpiozero import OutputDevice
import time

# =========================
# RELAY CONFIG
# =========================
RELAY_PIN = 17

# active_high=False = active LOW relay
relay = OutputDevice(RELAY_PIN, active_high=False, initial_value=False)

print("Starting relay test... Ctrl+C to stop.")

while True:
    print("ON")
    relay.on()
    time.sleep(2)

    print("OFF")
    relay.off()
    time.sleep(2)
