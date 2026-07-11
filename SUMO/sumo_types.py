from dataclasses import dataclass

@dataclass
class SUMOTrip:
    vehId: float
    tripId: float

    startLatitude: float
    startLongitude: float
    endLatitude: float
    endLongitude: float

    startSpeed: float
    endSpeed: float
