import pandas as pd

from SUMO.sumo_types import SUMOTrip
from SUMO.sumo_processes import runDuarouter, runSUMO
from SUMO.sumo_xml import generateSUMOTrip

def runSimulations(trips: pd.DataFrame):
    for trip in trips.to_dict(orient="records"):
        generateSUMOTrip(SUMOTrip(
            vehId=trip["VehId"],
            tripId=trip["Trip"],
            startLatitude=trip["startLatitude"],
            startLongitude=trip["startLongitude"],
            endLatitude=trip["endLatitude"],
            endLongitude=trip["endLongitude"],
            startSpeed=trip["startSpeed"],
            endSpeed=trip["endSpeed"],
        ))
