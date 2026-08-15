import math
import pandas as pd

from arguments import args
from custom_types import GPSPoint, SUMOTrip, SUMOVehicleExtraData

from SUMO.sumo_processes import runDuarouter, runSUMO
from SUMO.sumo_utils import loadSUMONetwork
from SUMO.sumo_xml import setupConfigs, generateSUMOTrips, addExtraToSUMOVehicles, getMaxTripDuration, readSUMOBatteryOut, getSUMOSimulationStats

def runSimulation(trajectories: pd.DataFrame, departDelay: float | None = None, SUMOvehicleTypes: dict[float, str] | None = None):
    # If it is not a validation execution, configure both SUMO and duarouter config files
    if not args.validation:
        setupConfigs(args.dataset)

    # Generate routes if requested
    if (args.generate_ruotes):
        sumoTrips: list[SUMOTrip] = []
        vehiclesExtra: dict[str, SUMOVehicleExtraData] = {}

        # Set currentDepart
        currentDepart: int = 0

        # If it's None, set departDelay using last simulation max trip duration
        if departDelay is None:
            departDelay = math.ceil(getMaxTripDuration()) + 30

        # Iterate over dataset trip records and for each generate SUMO trip data and SUMO vehicle extra data
        for trajectory in trajectories.to_dict(orient="records"):
            sumoVehicleId = trajectory["trajectoryId"]

            startpoint: GPSPoint = trajectory['startpoint']
            endpoint: GPSPoint = trajectory['endpoint']
            waypoints: list[GPSPoint] = trajectory["waypoints"]

            sumoTrips.append(SUMOTrip(
                id=sumoVehicleId,
                type=(
                    SUMOvehicleTypes.get(sumoVehicleId, "ev_generic")

                    if SUMOvehicleTypes is not None
                    else "ev_generic"
                ),

                depart=currentDepart,

                fromLonLat=f"{startpoint.longitude},{startpoint.latitude}",
                toLonLat=f"{endpoint.longitude},{endpoint.latitude}",
                viaLonLat=" ".join(
                    f"{waypoint.longitude},{waypoint.latitude}"
                    for waypoint in waypoints
                ),

                startSpeed=trajectory["startSpeed"],
                endSpeed=trajectory["endSpeed"],
            ))

            currentDepart += departDelay

            vehiclesExtra[sumoVehicleId] = SUMOVehicleExtraData(
                startpoint=trajectory["startpoint"],
                endpoint=trajectory["endpoint"],
                stops=trajectory["stops"]
            )

        # Load correct SUMO Network
        loadSUMONetwork()

        # Generate custom.trips.xml containing SUMO trips
        generateSUMOTrips(sumoTrips)

        # Run duarouter process to generate custom.rou.xml
        runDuarouter()

        # Add some additional properties to SUMO vehicles into custom.rou.xml
        addExtraToSUMOVehicles(vehiclesExtra)

    # Start SUMO simulation
    runSUMO()

    # If it was a validation execution, return battery data output by reading tripinfos.xml and other statistics about simulation
    if (args.validation):
        return readSUMOBatteryOut(), getSUMOSimulationStats()
    else:
        return
