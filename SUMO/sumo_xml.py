import xml.etree.ElementTree as ET

from SUMO.sumo_paths import CUSTOM
from SUMO.sumo_types import SUMOTrip

# Adds trips to custom.trips.xml
def addSUMOTrips(sumoTrips: list[SUMOTrip]):
    customTripsXml = ET.parse(CUSTOM / "custom.trips.xml")
    routes = customTripsXml.getroot()

    for trip in sumoTrips:
        routes.append(ET.Element("trip", {
            "id": trip.id,
            "type": trip.type,

            "depart": str(trip.depart),

            "fromLonLat": trip.fromLonLat,
            "toLonLat": trip.toLonLat,

            "departSpeed": str(trip.startSpeed),
            "arrivalSpeed": str(trip.endSpeed),
        }))

    customTripsXml.write(
        CUSTOM / "custom.trips.xml",
        encoding="utf-8",
        xml_declaration=True,
    )

def enrichSUMORoutes():
    return  # Placeholder
    # Must add:
    # - departPos - calculateRelativeOffset first edge
    # - arrivalPos - calculateRelativeOffset last edge
    # - stops - dict of SUMOStops, tripId as index

def readBatteryOut():
    return  # Placeholder
