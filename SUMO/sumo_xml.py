import math
import shutil
import xml.etree.ElementTree as ET

from paths import VALIDATION_CONFIG, VALIDATION_CUSTOM, VALIDATION_OUTPUT, CONFIG, CUSTOM, OUTPUT
from arguments import args
from custom_types import SUMOTrip, SUMOVehicleExtraData, SUMOBatteryData, SUMOSimStats

from SUMO.sumo_utils import getLanePositionOnEdge, getLanePositionFromEdgeList

configPath = VALIDATION_CONFIG if args.validation else CONFIG
customPath = VALIDATION_CUSTOM if args.validation else CUSTOM
outputPath = VALIDATION_OUTPUT if args.validation else OUTPUT

# Setup both SUMO and duarouter config files based on the specified dataset
def setupConfigs(datasetName: str = "dataset"):
    datasetCustomPath = customPath / datasetName
    datasetOutputPath = outputPath / datasetName

    # Recreate dataset-specific directories
    for path in [datasetCustomPath, datasetOutputPath]:
        if path.exists():
            shutil.rmtree(path)

        path.mkdir(parents=True)

    setupSUMOConfig(datasetName)
    setupDuarouterConfig(datasetName)

# Sets up SUMO config files based on the specified dataset
def setupSUMOConfig(datasetName: str = "dataset"):
    sumoConfigFilePath = configPath / "dataset.sumocfg"

    # Parse SUMO configuration
    sumoConfigFile = ET.parse(sumoConfigFilePath)
    sumoConfiguration = sumoConfigFile.getroot()

    # Retrieve configuration elements
    inputConfig = sumoConfiguration.find("./input")
    outputConfig = sumoConfiguration.find("./output")

    if inputConfig is None:
        raise RuntimeError("Could not find input section in dataset.sumocfg")

    if outputConfig is None:
        raise RuntimeError("Could not find output section in dataset.sumocfg")

    netFile = inputConfig.find("./net-file")
    routeFiles = inputConfig.find("./route-files")
    tripInfoOutput = outputConfig.find("./tripinfo-output")

    if netFile is None:
        raise RuntimeError("Could not find net-file in dataset.sumocfg")

    if routeFiles is None:
        raise RuntimeError("Could not find route-files in dataset.sumocfg")

    if tripInfoOutput is None:
        raise RuntimeError("Could not find tripinfo-output in dataset.sumocfg")

    # Configure dataset-specific paths
    netFile.set(
        "value",
        f"./{datasetName}/{datasetName}_3D.net.xml"
    )

    routeFiles.set(
        "value",
        f"../custom/{datasetName}/custom.rou.xml"
    )

    tripInfoOutput.set(
        "value",
        f"../output/{datasetName}/tripinfos.xml"
    )

    # Save updated configuration
    sumoConfigFile.write(
        sumoConfigFilePath,
        encoding="UTF-8",
        xml_declaration=True
    )

# Sets up duarouter config file based on specified dataset
def setupDuarouterConfig(datasetName: str = "dataset"):
    duarouterConfigFilePath = customPath / "custom.duarcfg"

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

    # Configure dataset-specific paths
    netFile.set(
        "value",
        f"../config/{datasetName}/{datasetName}_3D.net.xml"
    )

    outputFile.set(
        "value",
        f"./{datasetName}/custom.rou.xml"
    )

    # Save updated configuration
    duarouterConfigFile.write(
        duarouterConfigFilePath,
        encoding="UTF-8",
        xml_declaration=True
    )

# Generate custom.trips.xml and add trips to it
def generateSUMOTrips(sumoTrips: list[SUMOTrip]):
    customTripsPath = customPath / "custom.trips.xml"

    # Remove previous trip generation if present
    if customTripsPath.exists():
        customTripsPath.unlink()

    # Create new trips file
    routes = ET.Element("routes")
    customTripsXml = ET.ElementTree(routes)

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

    customTripsXml.write(
        customTripsPath,
        encoding="utf-8",
        xml_declaration=True,
    )

# Adds some additional properties to vehicles into custom.rou.xml
def addExtraToSUMOVehicles(vehiclesExtra: dict[str, SUMOVehicleExtraData]):
    customRoutesXmlPath = (
        customPath / "custom.rou.xml"
        if args.validation
        else customPath / args.dataset / "custom.rou.xml"
    )

    customRoutesXml = ET.parse(customRoutesXmlPath)
    routes = customRoutesXml.getroot()

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

    customRoutesXml.write(
        customRoutesXmlPath,
        encoding="utf-8",
        xml_declaration=True,
    )

# Returns the duration of the longest trip resulted after a simulation
def getMaxTripDuration():
    try:
        tripInfosXml = ET.parse(outputPath / "tripinfos.xml")
        tripinfos = tripInfosXml.getroot()

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

    tripInfosXml = ET.parse(outputPath / "tripinfos.xml")
    tripinfos = tripInfosXml.getroot()

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
    # Count generated trips
    tripsXml = ET.parse(customPath / "custom.trips.xml")
    trips = tripsXml.getroot().findall("trip")
    generatedTrips = len(trips)

    # Count vehicles generated by duarouter
    routesXml = ET.parse(customPath / "custom.rou.xml")
    vehicles = routesXml.getroot().findall("vehicle")
    generatedVehicles = len(vehicles)

    # Count vehicles actually simulated
    tripInfosXml = ET.parse(outputPath / "tripinfos.xml")
    tripinfos = tripInfosXml.getroot().findall("tripinfo")
    simulatedVehicles = len(tripinfos)

    return SUMOSimStats(
        generatedTrips=generatedTrips,
        generatedVehicles=generatedVehicles,
        simulatedVehicles=simulatedVehicles,

        discardedByDuarouter=generatedTrips - generatedVehicles,
        failedSimulation=generatedVehicles - simulatedVehicles
    )
