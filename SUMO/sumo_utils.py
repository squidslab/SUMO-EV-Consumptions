import math
from sumolib.net import readNet
from sumolib.net.lane import Lane

from SUMO.sumo_paths import CONFIG

# Retrieve SUMO network
net = readNet(str(CONFIG / "osm.net.xml.gz"))

# Converts GPS coordinates to SUMO coordinate system
def convertLonLatToSumoCoords(lat: float, lon: float):
    return net.convertLonLat2XY(lon, lat)

# Returns nearest lane for given GPS coordinates
def getNearestLane(lat: float, lon: float):
    # Convert GPS coordinates to the SUMO coordinate system
    x, y = convertLonLatToSumoCoords(lat, lon)

    # Retrieve all lanes located within a 50-meter radius of the specified SUMO coordinates
    neighbors = net.getNeighboringLanes(x, y, r=50)
    if not neighbors:
        raise RuntimeError("No lanes found within the specified radius.")

    # Find the nearest lane
    return min(neighbors, key=lambda item: item[1])[0]

# Returns the relative offset (in meters, measured from the beginning of the lane) of the specified GPS coordinates along specified lane or the nearest lane
def calculateRelativeOffset(lat: float, lon: float, lane: Lane | None = None):
    # Convert GPS coordinates to the SUMO coordinate system
    x, y = convertLonLatToSumoCoords(lat, lon)

    # Retrieve the nearest lane if necessary
    if lane is None:
        lane = getNearestLane(lat, lon)

    # Retrieve considered lane polyline representation
    shape = lane.getShape()

    # Track the closest projection on the lane and its corresponding offset
    bestOffset = 0.0
    bestDist = float("inf")
    lengthSoFar = 0.0

    # Iterate over each segment composing the lane shape
    for (x1, y1), (x2, y2) in zip(shape[:-1], shape[1:]):
        dx = x2 - x1
        dy = y2 - y1
        seg_len2 = dx * dx + dy * dy

        if seg_len2 == 0:
            continue

        # Project the point onto the current segment
        t = ((x - x1) * dx + (y - y1) * dy) / seg_len2
        t = max(0.0, min(1.0, t))

        proj_x = x1 + t * dx
        proj_y = y1 + t * dy

        # Compute the distance between the point and its projection
        dist = math.hypot(x - proj_x, y - proj_y)

        # Keep the projection with the minimum distance
        if dist < bestDist:
            bestDist = dist
            bestOffset = lengthSoFar + t * math.sqrt(seg_len2)

        # Update the cumulative distance from the beginning of the lane
        lengthSoFar += math.sqrt(seg_len2)

    return bestOffset
