import math
from sumolib.net import readNet
from sumolib.net.lane import Lane
from sumolib.net.edge import Edge

from paths import VALIDATION_CONFIG, CONFIG
from arguments import args
from custom_types import LanePosition

# Loads correct SUMO Network to achieve some calculations which requires reading it
def loadSUMONetwork():
    global net

    netPath = str(
        VALIDATION_CONFIG / "osm_3D.net.xml.gz" if args.validation
        else CONFIG / args.dataset / f"{args.dataset}_3D.net.xml"
    )

    net = readNet(netPath)

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

# Returns the elevation of GPS point projected onto the specified lane
def getElevationOnLane(lat: float, lon: float, lane: Lane):
    # Retrieve the relative offset of the GPS point along the lane
    offset, _ = projectPointOnLane(
        lat,
        lon,
        lane
    )

    # Retrieve specifed lane polyline representation in 3D
    shape = lane.getShape3D()

    # Track the cumulative distance from the beginning of the lane
    lengthSoFar = 0.0

    # Iterate over each segment composing the lane shape
    for point1, point2 in zip(shape[:-1], shape[1:]):
        x1, y1 = point1[:2]
        x2, y2 = point2[:2]

        segmentLength = math.hypot(
            x2 - x1,
            y2 - y1
        )

        if segmentLength == 0:
            continue

        segmentEnd = lengthSoFar + segmentLength

        # Check whether the projected point lies within the current segment
        if offset <= segmentEnd:
            # Calculate the relative position of the projected point within the current segment
            t = (
                offset - lengthSoFar
            ) / segmentLength

            # Retrieve the elevation at the beginning and end of the segment
            z1 = point1[2]
            z2 = point2[2]

            # Linearly interpolate the elevation at the projected point
            return z1 + t * (z2 - z1)

        # Update the cumulative distance from the beginning of the lane
        lengthSoFar = segmentEnd

    return None

# Returns the lane position (edge, lane, offset and distance) closest to the given GPS coordinates among the lanes of specified edge
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

# Returns the lane position (edge, lane, offset and distance) closest to the given GPS coordinates among a list of edges
def getLanePositionFromEdgeList(lat: float, lon: float, edgeIds: list[str]):
    bestLanePosition: LanePosition = None
    bestDistance = float("inf")

    currentLanePosition: LanePosition = None

    for edgeId in edgeIds:
        currentLanePosition = getLanePositionOnEdge(lat, lon, edgeId)

        if currentLanePosition is None:
            continue

        if currentLanePosition.distance < bestDistance:
            bestDistance = currentLanePosition.distance
            bestLanePosition = currentLanePosition

    return bestLanePosition

# Returns the lane position (edge, lane, offset and distance) closest to the given GPS coordinates within a certain radius
def getClosestLanePosition(lat: float, lon: float, radius: float = 30.0):
    x, y = convertLonLatToSumoCoords(lat, lon)

    edgeIds = [
        edge.getID()
        for edge, _ in net.getNeighboringEdges(
            x,
            y,
            radius
        )
    ]

    if not edgeIds:
        return None

    return getLanePositionFromEdgeList(
        lat,
        lon,
        edgeIds
    )

# Returns a map which associates every trajectory id with its sumo vehicle type
def mapSUMOVehicleTypes(otherIds: list[float], evedEVIds: list[float] = []):
    SUMOvehicleTypes: dict[float, str] = {}

    for trajectoryId in evedEVIds:
        SUMOvehicleTypes[trajectoryId] = "leaf_2013"

    for trajectoryId in otherIds:
        SUMOvehicleTypes[trajectoryId] = "ev_generic"

    return SUMOvehicleTypes

# Estimates the MAE and RMSE between dataset and SUMO elevations
def estimateSUMOElevationError(elevationStats: dict[tuple[float, float], float], stopAfter: int = 10000):
    absoluteErrors = []
    squaredErrors = []

    # Initialize stopping mechanism
    recordCount: int = 0
    print("Estimation will stop after:", stopAfter, "records")

    for (lat, lon), datasetElevation in elevationStats.items():
        # Find the closest lane within the default radius of 30 meters
        closestLanePosition = getClosestLanePosition(lat, lon)

        if closestLanePosition is None:
            continue

        # Retrieve SUMO elevation at the projected GPS point
        SUMOElevation = getElevationOnLane(lat, lon, closestLanePosition.lane)

        if SUMOElevation is None:
            continue

        # Calculate elevation error
        error = SUMOElevation - datasetElevation

        absoluteErrors.append(abs(error))
        squaredErrors.append(error ** 2)

        # Handle stopping mechanism
        recordCount += 1
        print(f"\rProcessed records: {recordCount}", end="", flush=True)

        if recordCount >= stopAfter:
            break

    # Print an empty line to separate upcoming outputs
    print()

    if not absoluteErrors:
        return None

    # Calculate Mean Absolute Error
    mae = sum(absoluteErrors) / len(absoluteErrors)

    # Calculate Root Mean Square Error
    rmse = math.sqrt(
        sum(squaredErrors) / len(squaredErrors)
    )

    return {
        "MAE": mae,
        "RMSE": rmse
    }
