import gpsd


class GPSService:
    def __init__(self):
        gpsd.connect()

    def get_position(self):
        try:
            packet = gpsd.get_current()

            # No valid fix yet
            if packet.mode < 2:
                return None, None

            lat = packet.lat
            lon = packet.lon

            # Reject empty/default coordinates
            if lat is None or lon is None:
                return None, None

            if lat == 0.0 and lon == 0.0:
                return None, None

            return lat, lon

        except Exception as e:
            print(f"GPS error: {e}")
            return None, None
