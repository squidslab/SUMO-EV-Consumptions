import math
import pandas as pd

from SUMO.sumo_types import SUMOTrip, SUMOVehicleExtraData
from SUMO.sumo_processes import runDuarouter, runSUMO
from SUMO.sumo_xml import addSUMOTrips, addExtraToSUMOVehicles, getMaxTripDuration, readSUMOBatteryOut, getSUMOSimulationStats

def runSimulation(trips: pd.DataFrame, SUMOvehicleTypes: dict[float, str], departDelay=None):
    sumoTrips: list[SUMOTrip] = []
    vehiclesExtra: dict[str, SUMOVehicleExtraData] = {}

    # Set currentDepart
    currentDepart: int = 0

    # If it's None, set departDelay using last simulation max trip duration
    if departDelay is None:
        departDelay = math.ceil(getMaxTripDuration()) + 30

    # Iterate over dataset trip records and for each generate SUMO trip data and SUMO vehicle extra data
    for trip in trips.to_dict(orient="records"):
        sumoVehicleId = trip["trajectoryId"]

        startpoint = trip['startpoint']
        endpoint = trip['endpoint']

        sumoTrips.append(SUMOTrip(
            id=sumoVehicleId,
            type=SUMOvehicleTypes[trip['vehId']],

            depart=currentDepart,

            fromLonLat=f"{startpoint['longitude']},{startpoint['latitude']}",
            toLonLat=f"{endpoint['longitude']},{endpoint['latitude']}",
            viaLonLat=" ".join(
                f"{waypoint['longitude']},{waypoint['latitude']}"
                for waypoint in trip["waypoints"]
            ),

            startSpeed=trip["startSpeed"],
            endSpeed=trip["endSpeed"],
        ))

        currentDepart += departDelay

        vehiclesExtra[sumoVehicleId] = SUMOVehicleExtraData(
            startpoint=trip["startpoint"],
            endpoint=trip["endpoint"],
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
