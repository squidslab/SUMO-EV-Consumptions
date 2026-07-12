from dataclasses import dataclass
from sumolib.net.lane import Lane
from sumolib.net.edge import Edge

@dataclass
class LanePosition:
    edge: Edge
    lane: Lane
    offset: float
    distance: float

@dataclass
class SUMOTrip:
    id: str
    type: str

    depart: int

    fromLonLat: str
    toLonLat: str

    startSpeed: float
    endSpeed: float

@dataclass
class SUMOVehicleExtraData:
    id: str

    startLatitude: float
    startLongitude: float
    endLatitude: float
    endLongitude: float

    stops: list[dict[str, float]]

@dataclass
class SUMOStop:
    lane: str
    duration: float
