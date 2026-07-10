import pandas as pd
from datetime import datetime

from datasets.dataset_utils import getDatasetEV

# Retrieve eVED, containing only electric vehicles
eVEDFiles = getDatasetEV(include=["EV"], entire=False)
eVED = pd.concat(
    list(map(lambda datasetFile: datasetFile.data, eVEDFiles)),
    ignore_index=True
)

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

def getTripStats():
    # Calculate some statistics for each vehicle-trip pair
    return eVED.groupby(["VehId", "Trip"]).agg(
        avgSpeed=("Vehicle Speed[km/h]", lambda speed: speed.mean() / 3.6),
        maxSpeed=("Vehicle Speed[km/h]", lambda speed: speed.max() / 3.6),
        totalEnergy=("Energy_Consumption", lambda energy: energy.sum() * 1000),
    ).reset_index()

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
