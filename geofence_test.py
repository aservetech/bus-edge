import time
import math

GEOFENCE_LAT = 40.7420
GEOFENCE_LON = -84.1052
RADIUS_METERS = 100

def distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

lat = 40.7410
lon = -84.1065
inside_geofence = False

while True:
    dist = distance_meters(lat, lon, GEOFENCE_LAT, GEOFENCE_LON)
    is_inside = dist < RADIUS_METERS

    print(f"Current: {lat}, {lon} | Distance: {int(dist)}m")

    if is_inside and not inside_geofence:
        print("🚨 ENTERED GEOFENCE 🚨")

    if not is_inside and inside_geofence:
        print("✅ EXITED GEOFENCE")

    inside_geofence = is_inside

    lat += 0.0001
    lon += 0.0001

    time.sleep(1)
