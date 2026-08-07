from dataclasses import dataclass
from sumolib.net.lane import Lane
from sumolib.net.edge import Edge
import pandas as pd

@dataclass
class DatasetFile:
    name: str
    data: pd.DataFrame

@dataclass
class GPSPoint:
    latitude: float
    longitude: float

@dataclass
class StopPoint:
    point: GPSPoint
    duration: float  # Seconds

@dataclass
class TrajectorySample:
    point: GPSPoint
    timestamp: float | None = None  # Milliseconds
    speed: float | None = None

@dataclass
class Trajectory:
    trajectoryId: str
    samples: list[TrajectorySample]

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
    viaLonLat: str

    startSpeed: float
    endSpeed: float

@dataclass
class SUMOVehicleExtraData:
    startpoint: GPSPoint
    endpoint: GPSPoint
    stops: list[StopPoint]

@dataclass
class SUMOBatteryData:
    totalEnergyConsumed: float

@dataclass
class SUMOSimStats:
    generatedTrips: int
    generatedVehicles: int
    simulatedVehicles: int

    discardedByDuarouter: int
    failedSimulation: int
