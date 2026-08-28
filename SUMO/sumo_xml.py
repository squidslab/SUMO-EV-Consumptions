import shutil
import math
import xml.etree.ElementTree as ET

from arguments import args
from custom_types import SUMOTrip, SUMOVehicleExtraData, SUMOBatteryData, SUMOSimStats

from SUMO.sumo_paths import configPath, customPath, outputPath
from SUMO.sumo_utils import getLanePositionOnEdge, getLanePositionFromEdgeList, mapSUMOVehicleTypes

# Sets up SUMO config files based on the specified scenario
def setupSUMOConfig():
    scenarioName = args.scenario_name

    sumoConfigFilePath = configPath / "scenario.sumocfg"
    scenarioOutputPath = outputPath / scenarioName

    # Remove scenario-specific output directory if it exists
    if scenarioOutputPath.exists():
        shutil.rmtree(scenarioOutputPath)

    # Create scenario-specific output directory
    scenarioOutputPath.mkdir(parents=True)

    # Parse SUMO configuration
    sumoConfigFile = ET.parse(sumoConfigFilePath)
    sumoConfiguration = sumoConfigFile.getroot()

    # Retrieve configuration elements
    inputConfig = sumoConfiguration.find("./input")
    outputConfig = sumoConfiguration.find("./output")

    if inputConfig is None:
        raise RuntimeError("Could not find input section in scenario.sumocfg")

    if outputConfig is None:
        raise RuntimeError("Could not find output section in scenario.sumocfg")

    netFile = inputConfig.find("./net-file")
    routeFiles = inputConfig.find("./route-files")
    tripInfoOutput = outputConfig.find("./tripinfo-output")

    if netFile is None:
        raise RuntimeError("Could not find net-file in scenario.sumocfg")

    if routeFiles is None:
        raise RuntimeError("Could not find route-files in scenario.sumocfg")

    if tripInfoOutput is None:
        raise RuntimeError(
            "Could not find tripinfo-output in scenario.sumocfg")

    # Configure scenario-specific paths
    netFile.set(
        "value",
        f"./{scenarioName}/{scenarioName}_3D.net.xml"
    )

    routeFiles.set(
        "value",
        f"../custom/{scenarioName}/custom.rou.xml"
    )

    tripInfoOutput.set(
        "value",
        f"../output/{scenarioName}/tripinfos.xml"
    )

    # Save updated configuration
    sumoConfigFile.write(
        sumoConfigFilePath,
        encoding="UTF-8",
        xml_declaration=True
    )

# Sets up duarouter config file based on specified scenario
def setupDuarouterConfig():
    scenarioName = args.scenario_name

    duarouterConfigFilePath = customPath / "custom.duarcfg"
    scenarioCustomPath = customPath / scenarioName

    # Remove scenario-specific custom directory if it exists
    if scenarioCustomPath.exists():
        shutil.rmtree(scenarioCustomPath)

    # Create scenario-specific custom directory
    scenarioCustomPath.mkdir(parents=True)

    # Parse duarouter configuration
    duarouterConfigFile = ET.parse(duarouterConfigFilePath)
    duarouterConfiguration = duarouterConfigFile.getroot()

    # Retrieve configuration elements
    inputConfig = duarouterConfiguration.find("./input")
    outputConfig = duarouterConfiguration.find("./output")

    if inputConfig is None:
        raise RuntimeError("Could not find input section in custom.duarcfg")

    if outputConfig is None:
        raise RuntimeError("Could not find output section in custom.duarcfg")

    netFile = inputConfig.find("./net-file")
    outputFile = outputConfig.find("./output-file")

    if netFile is None:
        raise RuntimeError("Could not find net-file in custom.duarcfg")

    if outputFile is None:
        raise RuntimeError("Could not find output-file in custom.duarcfg")

    # Configure scenario-specific paths
    netFile.set(
        "value",
        f"../config/{scenarioName}/{scenarioName}_3D.net.xml"
    )

    outputFile.set(
        "value",
        f"./{scenarioName}/custom.rou.xml"
    )

    # Save updated configuration
    duarouterConfigFile.write(
        duarouterConfigFilePath,
        encoding="UTF-8",
        xml_declaration=True
    )

# Generate custom.trips.xml and add trips to it
def generateSUMOTrips(sumoTrips: list[SUMOTrip]):
    customTripsFilePath = customPath / "custom.trips.xml"

    # Remove previous trip generation if present
    if customTripsFilePath.exists():
        customTripsFilePath.unlink()

    # Create new trips file
    routes = ET.Element("routes")
    customTripsFile = ET.ElementTree(routes)

    # Generate sumo trips
    for sumoTrip in sumoTrips:
        attributes = {
            "id": sumoTrip.id,
            "type": sumoTrip.type,

            "depart": str(sumoTrip.depart),

            "fromLonLat": sumoTrip.fromLonLat,
            "toLonLat": sumoTrip.toLonLat,
            "viaLonLat": sumoTrip.viaLonLat,
        }

        if not math.isnan(sumoTrip.startSpeed):
            attributes["departSpeed"] = str(sumoTrip.startSpeed)

        if not math.isnan(sumoTrip.endSpeed):
            attributes["arrivalSpeed"] = str(sumoTrip.endSpeed)

        routes.append(ET.Element("trip", attributes))

    customTripsFile.write(
        customTripsFilePath,
        encoding="utf-8",
        xml_declaration=True,
    )

# Adds some additional properties to vehicles into custom.rou.xml
def addExtraToSUMOVehicles(vehiclesExtra: dict[str, SUMOVehicleExtraData]):
    customRoutesFilePath = (
        customPath / "custom.rou.xml" if args.validation
        else customPath / args.scenario_name / "custom.rou.xml"
    )

    customRoutesFile = ET.parse(customRoutesFilePath)
    routes = customRoutesFile.getroot()

    # Iterate over each vehicle inside routes element
    for vehicle in routes.findall("vehicle"):
        # Retrieve vehicle id and edges that constitutes its route
        sumoVehicleId = vehicle.get("id")
        edges = vehicle.find("route").get("edges").split()

        # Calculate precise departPos as an offset from the begginning of the lane closest to GPS point on the first edge
        departPos = getLanePositionOnEdge(
            vehiclesExtra[sumoVehicleId].startpoint.latitude,
            vehiclesExtra[sumoVehicleId].startpoint.longitude,
            edges[0]
        ).offset

        # Calculate precise arrivalPos as an offset from the begginning of the lane closest to GPS point on the last edge
        arrivalPos = getLanePositionOnEdge(
            vehiclesExtra[sumoVehicleId].endpoint.latitude,
            vehiclesExtra[sumoVehicleId].endpoint.longitude,
            edges[-1]
        ).offset

        # Set calculated departPos and arrivalPos
        vehicle.set("departPos", str(departPos))
        vehicle.set("arrivalPos", str(arrivalPos))

        # Add each stop to the vehicle
        for stop in vehiclesExtra[sumoVehicleId].stops:
            stopLane = getLanePositionFromEdgeList(
                stop.point.latitude,
                stop.point.longitude,
                edges
            ).lane.getID()

            vehicle.append(
                ET.Element("stop", {
                    "lane": stopLane,
                    "duration": str(stop.duration)
                })
            )

    customRoutesFile.write(
        customRoutesFilePath,
        encoding="utf-8",
        xml_declaration=True,
    )

# Adds missing depart times and vehicle types to randomly generated vehicles into custom.rou.xml
def finalizeRandomSUMOVehicles(randomizeVehTypes: bool, departDelay: float):
    customRoutesFilePath = (
        customPath / "custom.rou.xml" if args.validation
        else customPath / args.scenario_name / "custom.rou.xml"
    )

    customRoutesFile = ET.parse(customRoutesFilePath)
    routes = customRoutesFile.getroot()
    vehicles = routes.findall("vehicle")

    # Assign a SUMO vehicle type to each vehicle into custom.rou.xml
    vehicleIds = [vehicle.get("id")for vehicle in vehicles]

    SUMOvehicleTypes = mapSUMOVehicleTypes(
        vehicleIds, randomize=randomizeVehTypes
    )

    # Set current depart
    currentDepart: float = 0.00

    # Iterate over each vehicle and assign type and depart
    for vehicle in vehicles:
        vehicle.set("type", SUMOvehicleTypes[vehicle.get("id")])
        vehicle.set("depart", str(currentDepart))

        # Increment current depart based on specified delay
        currentDepart += departDelay

    customRoutesFile.write(
        customRoutesFilePath,
        encoding="utf-8",
        xml_declaration=True,
    )

# Returns the duration of the longest trip resulted after a simulation
def getMaxTripDuration():
    try:
        tripInfosFile = ET.parse(outputPath / "tripinfos.xml")
        tripinfos = tripInfosFile.getroot()

        maxDuration = None

        for tripinfo in tripinfos.findall("tripinfo"):
            duration = float(tripinfo.get("duration"))

            if maxDuration is None or duration > maxDuration:
                maxDuration = duration

        return maxDuration if maxDuration is not None else 970.0
    except Exception:
        return 970.0

# Reads tripinfos.xml to return resulting battery data generated by a simulation
def readSUMOBatteryOut():
    batteryData: dict[str, SUMOBatteryData] = {}
    tripInfosFilePath = (
        outputPath / "tripinfos.xml" if args.validation
        else outputPath / args.scenario_name / "tripinfos.xml"
    )

    tripInfosFile = ET.parse(tripInfosFilePath)
    tripinfos = tripInfosFile.getroot()

    for tripinfo in tripinfos.findall("tripinfo"):
        tripinfoId = tripinfo.get("id")

        batteryData[tripinfoId] = SUMOBatteryData(
            totalEnergyConsumed=float(
                tripinfo.find("battery").get("totalEnergyConsumed")
            )
        )

    return batteryData

# Reads custom.trips.xml, custom.rou.xml and tripinfos.xml to generate some stats about last simulation
def getSUMOSimulationStats():
    customTripsFilePath = (
        customPath / "custom.trips.xml" if args.scenario == "dataset"
        else customPath / "trips.trips.xml"
    )

    customRoutesFilePath = (
        customPath / "custom.rou.xml" if args.validation
        else customPath / args.scenario_name / "custom.rou.xml"
    )

    tripInfosFilePath = (
        outputPath / "tripinfos.xml" if args.validation
        else outputPath / args.scenario_name / "tripinfos.xml"
    )

    # Count generated trips
    customTripsFile = ET.parse(customTripsFilePath)
    trips = customTripsFile.getroot().findall("trip")
    generatedTrips = len(trips)

    # Count vehicles generated by duarouter
    customRoutesFile = ET.parse(customRoutesFilePath)
    vehicles = customRoutesFile.getroot().findall("vehicle")
    generatedVehicles = len(vehicles)

    # Count vehicles actually simulated
    tripInfosFile = ET.parse(tripInfosFilePath)
    tripinfos = tripInfosFile.getroot().findall("tripinfo")
    simulatedVehicles = len(tripinfos)

    return SUMOSimStats(
        generatedTrips=generatedTrips,
        generatedVehicles=generatedVehicles,
        simulatedVehicles=simulatedVehicles,

        discardedByDuarouter=generatedTrips - generatedVehicles,
        failedSimulation=generatedVehicles - simulatedVehicles
    )
