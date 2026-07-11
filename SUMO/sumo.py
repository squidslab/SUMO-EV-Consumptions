import pandas as pd

from SUMO.sumo_types import SUMOTrip
from SUMO.sumo_processes import runDuarouter, runSUMO
from SUMO.sumo_xml import addSUMOTrips

def runSimulations(trips: pd.DataFrame):
    sumoTrips: list[SUMOTrip] = []
    currentDepart: int = 0

    # Iterate over dataset trip records and for each generate SUMO trip data
    for trip in trips.to_dict(orient="records"):
        sumoTrips.append(SUMOTrip(
            id=f"{trip['VehId']}_{trip['Trip']}",
            type="leaf_2013",

            depart=currentDepart,

            fromLonLat=f"{trip['startLongitude']},{trip['startLatitude']}",
            toLonLat=f"{trip['endLongitude']},{trip['endLatitude']}",

            startSpeed=trip["startSpeed"],
            endSpeed=trip["endSpeed"],
        ))

        currentDepart = currentDepart + 10000

    # Add SUMO trips to custom.trips.xml
    addSUMOTrips(sumoTrips)

    # Run duarouter process to generate custom.rou.xml
    runDuarouter()
