import pandas as pd
from datetime import datetime

from arguments import args

from datasets.dataset_data import getDatasetEV
from datasets.dataset_utils import calculateTripDistance, findStops, findWaypoints

# Retrieve eVED, containing only electric vehicles
eVEDFiles = getDatasetEV(include=args.vehicle_types, entire=False)
eVED = pd.concat(
    list(map(lambda datasetFile: datasetFile.data, eVEDFiles)),
    ignore_index=True
).sort_values(["DayNum", "VehId", "Trip", "Timestamp(ms)"])

def getDatasetStats():
    # Calculate dataset global stats
    return {
        "samples": len(eVED),
        "vehicles": eVED["VehId"].nunique(),
        "trips": eVED["Trip"].nunique(),
        "minLatitude": float(eVED["Matchted Latitude[deg]"].min()),
        "maxLatitude": float(eVED["Matchted Latitude[deg]"].max()),
        "minLongitude": float(eVED["Matched Longitude[deg]"].min()),
        "maxLongitude": float(eVED["Matched Longitude[deg]"].max()),
    }

def getElevationStats():
    elevationStats = eVED[
        [
            "Matchted Latitude[deg]",
            "Matched Longitude[deg]",
            "Elevation Smoothed[m]",
        ]
    ].copy()

    return {
        (float(record["Matchted Latitude[deg]"]), float(record["Matched Longitude[deg]"])):
        float(record["Elevation Smoothed[m]"])
        for _, record in elevationStats.iterrows()
    }

def getVehStats():
    # Calculate number of trips per vehicle
    return eVED.groupby("VehId").agg(
        tripCount=("Trip", "nunique"),
        samplesCount=("Trip", "size")
    ).reset_index()

def getTripStats():
    tripStats = []

    for (vehId, tripId), trip in eVED.groupby(["VehId", "Trip"]):
        tripStats.append({
            "VehId": vehId,
            "Trip": tripId,

            "totalEnergyConsumed": (
                trip["Energy_Consumption"].sum() * 1000
            ),

            "startLatitude": (
                trip["Matchted Latitude[deg]"].iloc[0]
            ),
            "startLongitude": (
                trip["Matched Longitude[deg]"].iloc[0]
            ),

            "endLatitude": (
                trip["Matchted Latitude[deg]"].iloc[-1]
            ),
            "endLongitude": (
                trip["Matched Longitude[deg]"].iloc[-1]
            ),

            "startSpeed": (
                trip["Vehicle Speed[km/h]"].iloc[0] / 3.6
            ),
            "endSpeed": (
                trip["Vehicle Speed[km/h]"].iloc[-1] / 3.6
            ),

            "avgSpeed": (
                trip["Vehicle Speed[km/h]"].mean() / 3.6
            ),
            "maxSpeed": (
                trip["Vehicle Speed[km/h]"].max() / 3.6
            ),

            "distanceTraveled": (
                calculateTripDistance(trip)
            ),

            "stops": (
                findStops(trip)
            ),

            "waypoints": (
                findWaypoints(trip)
            )
        })

    return pd.DataFrame(tripStats)

def getDailyStats():
    # Convert DayNum values to integers, so that all samples belonging to the same day are grouped together
    dailyData = eVED.copy()
    dailyData["DayNum"] = dailyData["DayNum"].astype(int)

    # Calculate number of trips per day
    dailyStats = dailyData.groupby("DayNum").agg(
        tripCount=("Trip", "nunique"),
        samplesCount=("Trip", "size")
    ).reset_index()

    # Convert DayNum to datetime
    baseDate = pd.Timestamp("2017-11-01")
    dailyStats["Date"] = dailyStats["DayNum"].apply(
        lambda dayNum: baseDate + pd.Timedelta(days=dayNum - 1))

    return dailyStats


def getTripsWeeklyDistr():
    weeks = []
    tripCounts = []

    # Calculate how trips are distributed per week over the year covered by the dataset
    # Weeks and their respectives trip count are stored in different lists with matching indexes
    for datasetFile in eVEDFiles:
        weeks.append(
            datetime.strptime(datasetFile.name.split("_")[1], "%y%m%d")
        )
        tripCounts.append(datasetFile.data["Trip"].nunique())

    return {"weeks": weeks, "tripCounts": tripCounts}
