from dataclasses import dataclass

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
class SUMOStop:
    lane: str
    duration: float
