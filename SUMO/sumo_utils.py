import math
from sumolib.net import readNet
from sumolib.net.lane import Lane
from sumolib.net.edge import Edge

from SUMO.sumo_paths import CONFIG
from SUMO.sumo_types import LanePosition

# Retrieve SUMO network
net = readNet(str(CONFIG / "osm.net.xml.gz"))

# Converts GPS coordinates to SUMO coordinate system
def convertLonLatToSumoCoords(lat: float, lon: float):
    return net.convertLonLat2XY(lon, lat)

# Returns the relative offset (in meters, measured from the beginning of the lane) together with the distance between the GPS point and the lane
def projectPointOnLane(lat: float, lon: float, lane: Lane):
    x, y = convertLonLatToSumoCoords(lat, lon)

    # Retrieve specifed lane polyline representation
    shape = lane.getShape()

    # Track the closest projection on the lane and its corresponding offset
    bestOffset = 0.0
    bestDist = float("inf")
    lengthSoFar = 0.0

    # Iterate over each segment composing the lane shape
    for (x1, y1), (x2, y2) in zip(shape[:-1], shape[1:]):
        dx = x2 - x1
        dy = y2 - y1
        segLen2 = dx * dx + dy * dy

        if segLen2 == 0:
            continue

        # Project the point onto the current segment
        t = ((x - x1) * dx + (y - y1) * dy) / segLen2
        t = max(0.0, min(1.0, t))

        projX = x1 + t * dx
        projY = y1 + t * dy

        # Compute the distance between the point and its projection
        dist = math.hypot(x - projX, y - projY)

        if dist < bestDist:
            bestDist = dist
            bestOffset = lengthSoFar + t * math.sqrt(segLen2)

        # Update the cumulative distance from the beginning of the lan
        lengthSoFar += math.sqrt(segLen2)

    return bestOffset, bestDist


# Returns the lane of the specified edge that is closest to the given GPS coordinates along with its relative offset and minimum distance between the GPS point and the lane
def getLanePositionOnEdge(lat: float, lon: float, edgeId: str):
    edge: Edge = net.getEdge(edgeId)

    bestLanePosition: LanePosition = None
    bestDistance = float("inf")

    for lane in edge.getLanes():
        offset, distance = projectPointOnLane(lat, lon, lane)

        if distance < bestDistance:
            bestDistance = distance

            # Offset gets rounded up to two decimal places
            bestLanePosition = LanePosition(
                edge=edge,
                lane=lane,
                offset=math.ceil(offset * 100) / 100,
                distance=distance
            )

    return bestLanePosition

# Returns the lane position (edge, lane, offset and distance) closest to the given GPS coordinates among a list of edge ids
def getLanePositionFromEdgeList(lat: float, lon: float, edgeIds: list[str]):
    bestLanePosition: LanePosition = None
    bestDistance = float("inf")

    currentLanePosition: LanePosition = None

    for edgeId in edgeIds:
        currentLanePosition = getLanePositionOnEdge(lat, lon, edgeId)

        if currentLanePosition.distance < bestDistance:
            bestDistance = currentLanePosition.distance
            bestLanePosition = currentLanePosition

    return bestLanePosition
