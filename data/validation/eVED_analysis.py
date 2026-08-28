import pandas as pd
from datetime import datetime

from arguments import args
from custom_types import GPSPoint, TrajectorySample

from data.utils import findStops, findWaypoints
from data.validation.eVED_data import getDatasetEV

# Retrieve eVED, containing only electric vehicles
def loadEVED():
    global eVEDFiles, eVED

    eVEDFiles = getDatasetEV(include=args.eved_veh_types, entire=False)
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
        TrajectorySamples = [
            TrajectorySample(
                point=GPSPoint(
                    latitude=float(row["Matchted Latitude[deg]"]),
                    longitude=float(row["Matched Longitude[deg]"])
                ),
                timestamp=float(row["Timestamp(ms)"]),
                speed=float(row["Vehicle Speed[km/h]"] / 3.6)
            )
            for _, row in trip.iterrows()
        ]

        tripStats.append({
            "vehId": vehId,

            "tripId": tripId,

            "trajectoryId": f"{vehId}_{tripId}",

            "startpoint": TrajectorySamples[0].point,

            "endpoint": TrajectorySamples[-1].point,

            "waypoints": findWaypoints(TrajectorySamples),

            "startSpeed": TrajectorySamples[0].speed,

            "endSpeed": TrajectorySamples[-1].speed,

            "stops": findStops(TrajectorySamples),

            "totalEnergyConsumed": trip["Energy_Consumption"].sum() * 1000,
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
