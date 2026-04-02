import math


class GeofenceService:
    def __init__(self, geofence_lat: float, geofence_lon: float, radius_meters: float):
        self.geofence_lat = geofence_lat
        self.geofence_lon = geofence_lon
        self.radius_meters = radius_meters
        self.inside_geofence = False

    def distance_meters(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def check_position(self, lat: float, lon: float) -> dict:
        dist = self.distance_meters(lat, lon, self.geofence_lat, self.geofence_lon)
        is_inside = dist < self.radius_meters

        event = None
        if is_inside and not self.inside_geofence:
            event = "entered"
        elif not is_inside and self.inside_geofence:
            event = "exited"

        self.inside_geofence = is_inside

        return {
            "distance": dist,
            "inside": is_inside,
            "event": event,
        }
