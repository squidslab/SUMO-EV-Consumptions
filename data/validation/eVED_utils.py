import math
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2 +
        math.cos(phi1) *
        math.cos(phi2) *
        math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def calculateTripDistance(trip: pd.DataFrame):
    coords = zip(
        trip["Matchted Latitude[deg]"],
        trip["Matched Longitude[deg]"]
    )

    distance = 0.0
    previous = None

    for lat, lon in coords:
        if previous:
            distance += haversine(
                previous[0],
                previous[1],
                lat,
                lon
            )

        previous = (lat, lon)

    return distance

def findStops(trip: pd.DataFrame):
    stops = []

    # Ensure records are ordered by timestamp
    trip = trip.sort_values("Timestamp(ms)")

    # Identify records where vehicle is stopped
    stopped = trip["Vehicle Speed[km/h]"] == 0

    # Create groups of consecutive stopped records
    stopGroups = stopped.ne(stopped.shift()).cumsum()

    for _, group in trip[stopped].groupby(stopGroups[stopped]):
        startRecord = group.iloc[0]
        endRecord = group.iloc[-1]

        stops.append({
            "latitude": float(startRecord["Matchted Latitude[deg]"]),
            "longitude": float(startRecord["Matched Longitude[deg]"]),
            "duration": float((endRecord["Timestamp(ms)"] - startRecord["Timestamp(ms)"]) / 1000)
        })

    return stops

def findWaypoints(trip: pd.DataFrame, maxWaypoints: int = 15):
    records = trip.iloc[1:-1]

    if records.empty:
        return []

    distance = calculateTripDistance(trip)

    # One waypoint every 1000 meters, capped at 15
    waypointCount = min(
        maxWaypoints,
        max(0, math.floor(distance / 1000))
    )

    if waypointCount == 0:
        return []

    interval = max(1, len(records) // waypointCount)

    return [
        {
            "latitude": float(record["Matchted Latitude[deg]"]),
            "longitude": float(record["Matched Longitude[deg]"]),
        }
        for _, record in records.iloc[::interval].head(waypointCount).iterrows()
    ]
