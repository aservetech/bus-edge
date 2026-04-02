import gpsd
import time

gpsd.connect()

while True:
    try:
        packet = gpsd.get_current()
        if packet.mode >= 2:
            print(f"Lat: {packet.lat}, Lon: {packet.lon}, Satellites mode: {packet.mode}")
        else:
            print("GPS connected, waiting for fix...")
    except Exception as e:
        print(f"GPS read error: {e}")

    time.sleep(1)
