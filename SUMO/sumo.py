import pandas as pd

from SUMO.sumo_types import SUMOTrip, SUMOVehicleExtraData
from SUMO.sumo_processes import runDuarouter, runSUMO
from SUMO.sumo_xml import addSUMOTrips, enrichSUMORoutes

def runSimulation(trips: pd.DataFrame):
    sumoTrips: list[SUMOTrip] = []
    vehiclesExtra: list[SUMOVehicleExtraData] = []

    currentDepart: int = 0

    # Iterate over dataset trip records and for each generate SUMO trip data
    for trip in trips.to_dict(orient="records"):
        sumoVehicleId = f"{trip['VehId']}_{trip['Trip']}"

        sumoTrips.append(SUMOTrip(
            id=sumoVehicleId,
            type="leaf_2013",

            depart=currentDepart,

            fromLonLat=f"{trip['startLongitude']},{trip['startLatitude']}",
            toLonLat=f"{trip['endLongitude']},{trip['endLatitude']}",

            startSpeed=trip["startSpeed"],
            endSpeed=trip["endSpeed"],
        ))

        currentDepart = currentDepart + 1000

        vehiclesExtra.append(SUMOVehicleExtraData(
            id=sumoVehicleId,

            startLatitude=trip["startLatitude"],
            startLongitude=trip["startLongitude"],
            endLatitude=trip["endLatitude"],
            endLongitude=trip["endLongitude"],

            stops=trip["stops"]
        ))

    # Add SUMO trips to custom.trips.xml
    addSUMOTrips(sumoTrips)

    # Run duarouter process to generate custom.rou.xml
    runDuarouter()

    # Adds some properties to vehicles into routes file
    enrichSUMORoutes(vehiclesExtra)

    # Start SUMO simulation
    runSUMO()
