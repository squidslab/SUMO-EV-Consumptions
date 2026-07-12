import xml.etree.ElementTree as ET

from SUMO.sumo_paths import CUSTOM
from SUMO.sumo_types import SUMOTrip, SUMOVehicleExtraData, SUMOStop
from SUMO.sumo_utils import getLanePositionOnEdge, getLanePositionFromEdgeList

# Adds trips to custom.trips.xml
def addSUMOTrips(sumoTrips: list[SUMOTrip]):
    customTripsXml = ET.parse(CUSTOM / "custom.trips.xml")
    routes = customTripsXml.getroot()

    # Clean up previous trip generation if present
    if (routes.findall("trip")):
        for trip in routes.findall("trip"):
            routes.remove(trip)

    # Generate sumo trips
    for sumoTrip in sumoTrips:
        routes.append(ET.Element("trip", {
            "id": sumoTrip.id,
            "type": sumoTrip.type,

            "depart": str(sumoTrip.depart),

            "fromLonLat": sumoTrip.fromLonLat,
            "toLonLat": sumoTrip.toLonLat,

            "departSpeed": str(sumoTrip.startSpeed),
            "arrivalSpeed": str(sumoTrip.endSpeed),
        }))

    customTripsXml.write(
        CUSTOM / "custom.trips.xml",
        encoding="utf-8",
        xml_declaration=True,
    )

def enrichSUMORoutes(vehiclesExtra: list[SUMOVehicleExtraData]):
    vehiclesExtraMap = {
        vehicleExtra.id: vehicleExtra
        for vehicleExtra in vehiclesExtra
    }

    customRoutesXml = ET.parse(CUSTOM / "custom.rou.xml")
    routes = customRoutesXml.getroot()

    for vehicle in routes.findall("vehicle"):
        sumoVehicleId = vehicle.get("id")
        edges = vehicle.find("route").get("edges").split()

        departPos = getLanePositionOnEdge(
            vehiclesExtraMap[sumoVehicleId].startLatitude,
            vehiclesExtraMap[sumoVehicleId].startLongitude,
            edges[0]
        ).offset

        arrivalPos = getLanePositionOnEdge(
            vehiclesExtraMap[sumoVehicleId].endLatitude,
            vehiclesExtraMap[sumoVehicleId].endLongitude,
            edges[-1]
        ).offset

        vehicle.set("departPos", str(departPos))
        vehicle.set("arrivalPos", str(arrivalPos))

        for stop in vehiclesExtraMap[sumoVehicleId].stops:
            stopLane = getLanePositionFromEdgeList(
                stop["latitude"],
                stop["longitude"],
                edges
            ).lane.getID()

            vehicle.append(
                ET.Element("stop", {
                    "lane": stopLane,
                    "duration": str(stop["duration"])
                })
            )

    customRoutesXml.write(
        CUSTOM / "custom.rou.xml",
        encoding="utf-8",
        xml_declaration=True,
    )

def readBatteryOut():
    return  # Placeholder
