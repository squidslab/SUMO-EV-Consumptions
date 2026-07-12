import pandas as pd
from datetime import datetime

from datasets.dataset_utils import getDatasetEV

# Retrieve eVED, containing only electric vehicles
eVEDFiles = getDatasetEV(include=["EV"], entire=False)
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

def getVehStats():
    # Calculate number of trips per vehicle
    return eVED.groupby("VehId").agg(
        tripCount=("Trip", "nunique"),
        samplesCount=("Trip", "size")
    ).reset_index()

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

def getTripStats():
    # Calculate some statistics for each trip
    tripStats = eVED.groupby(["VehId", "Trip"]).agg(
        totalEnergy=("Energy_Consumption", lambda energy: energy.sum() * 1000),

        startLatitude=("Matchted Latitude[deg]", "first"),
        startLongitude=("Matched Longitude[deg]", "first"),

        endLatitude=("Matchted Latitude[deg]", "last"),
        endLongitude=("Matched Longitude[deg]", "last"),

        startSpeed=("Vehicle Speed[km/h]", lambda speed: speed.iloc[0] / 3.6),
        endSpeed=("Vehicle Speed[km/h]", lambda speed: speed.iloc[-1] / 3.6),

        avgSpeed=("Vehicle Speed[km/h]", lambda speed: speed.mean() / 3.6),
        maxSpeed=("Vehicle Speed[km/h]", lambda speed: speed.max() / 3.6),
    )

    # Calculate stops for each trip
    stops = (
        eVED
        .groupby(["VehId", "Trip"])
        .apply(findStops)
        .rename("stops")
    )

    return tripStats.join(stops).reset_index()

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
