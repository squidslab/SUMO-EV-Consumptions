import math
import pandas as pd

from SUMO.sumo_types import SUMOTrip, SUMOVehicleExtraData
from SUMO.sumo_processes import runDuarouter, runSUMO
from SUMO.sumo_xml import addSUMOTrips, addExtraToSUMOVehicles, getMaxTripDuration, readSUMOBatteryOut, getSUMOSimulationStats

def runSimulation(trips: pd.DataFrame, SUMOvehicleTypes: dict[float, str], maxTripDuration=math.ceil(getMaxTripDuration()) + 30):
    sumoTrips: list[SUMOTrip] = []
    vehiclesExtra: dict[str, SUMOVehicleExtraData] = {}

    # Set currentDepart
    currentDepart: int = 0

    # Iterate over dataset trip records and for each generate SUMO trip data and SUMO vehicle extra data
    for trip in trips.to_dict(orient="records"):
        sumoVehicleId = f"{trip['VehId']}_{trip['Trip']}"

        sumoTrips.append(SUMOTrip(
            id=sumoVehicleId,
            type=SUMOvehicleTypes[trip['VehId']],

            depart=currentDepart,

            fromLonLat=f"{trip['startLongitude']},{trip['startLatitude']}",
            toLonLat=f"{trip['endLongitude']},{trip['endLatitude']}",
            viaLonLat=" ".join(
                f"{waypoint['longitude']},{waypoint['latitude']}"
                for waypoint in trip["waypoints"]
            ),

            startSpeed=trip["startSpeed"],
            endSpeed=trip["endSpeed"],
        ))

        currentDepart += maxTripDuration

        vehiclesExtra[sumoVehicleId] = SUMOVehicleExtraData(
            startLatitude=trip["startLatitude"],
            startLongitude=trip["startLongitude"],
            endLatitude=trip["endLatitude"],
            endLongitude=trip["endLongitude"],

            stops=trip["stops"]
        )

    # Add SUMO trips to custom.trips.xml
    addSUMOTrips(sumoTrips)

    # Run duarouter process to generate custom.rou.xml
    runDuarouter()

    # Add some additional properties to SUMO vehicles into custom.rou.xml
    addExtraToSUMOVehicles(vehiclesExtra)

    # Start SUMO simulation
    runSUMO()

    # Return battery data output by reading tripinfos.xml and other statistics about simulation
    return readSUMOBatteryOut(), getSUMOSimulationStats()
