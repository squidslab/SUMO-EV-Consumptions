import re
import math
import json
import xml.etree.ElementTree as ET
import pandas as pd

from paths import VIRTUAL_DATASETS
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

def generateVirtualDatasetId(source: str):
    # Get current date in YYYYMMDD format
    date = datetime.now().strftime("%Y%m%d")

    # Search for existing datasets generated today
    pattern = re.compile(rf"{date}_{source}_(\d{{3}})\.csv")

    simulationNumbers = []
    for dataset in VIRTUAL_DATASETS.glob(f"{date}_{source}_*.csv"):
        match = pattern.match(dataset.name)

        if match:
            simulationNumbers.append(int(match.group(1)))

    # Generate the next progressive number
    nextNumber = max(simulationNumbers, default=0) + 1

    return f"{date}_{source}_{nextNumber:03d}"

# Generates a virtual dataset from SUMO tripinfo.xml obtained from a simulation
def generateVirtualDataset(tripInfosFilePath: Path, sourceScenario: str, trajectories: pd.DataFrame | None = None):
    # Parse SUMO tripinfos.xml at given path
    tripInfosFile = ET.parse(tripInfosFilePath / "tripinfos.xml")
    tripInfos = tripInfosFile.getroot()

    # Create trajectory metadata dictionary if original trajectories are available
    trajectoryMetadata = (
        {
            trajectory['trajectoryId']: trajectory
            for trajectory in trajectories.to_dict(orient="records")
        }
        if trajectories is not None
        else None
    )

    # Records to generate for virtual database
    virtualTrips = []

    # Extract data for each simulated trip
    for tripInfo in tripInfos.findall("tripinfo"):
        trajectoryId = tripInfo.get("id")

        # Retrieve original trajectory metadata if available
        trajectory = (
            trajectoryMetadata.get(trajectoryId)
            if trajectoryMetadata is not None
            else None
        )

        # Skip trips for which the original trajectory metadata cannot be found
        if trajectories is not None and trajectory is None:
            continue

        # Retrieve battery info
        battery = tripInfo.find("battery")

        # Skip trips without battery information
        if battery is None:
            continue

        # Add simulation-generated data
        virtualTrip = {
            "trajectoryId": trajectoryId,
            "vehicleType": tripInfo.get("vType"),

            "tripDuration (s)": float(tripInfo.get("duration", 0.0)),
            "tripDistance (m)": float(tripInfo.get("routeLength", 0.0)),
            "tripAvgSpeed (m/s)": math.ceil(float(tripInfo.get("routeLength")) / float(tripInfo.get("duration")) * 100) / 100,

            "batteryCapacity (Wh)": float(battery.get("actualBatteryCapacity", 0.0)),
            "energyConsumed (Wh)": float(battery.get("totalEnergyConsumed", 0.0)),
            "energyRegenerated (Wh)": float(battery.get("totalEnergyRegenerated", 0.0)),
        }

        # Add trajectory metadata when available
        if trajectory is not None:
            virtualTrip.update(
                {
                    "startpoint (lat, lon)": json.dumps(asdict(trajectory["startpoint"])),
                    "endpoint (lat, lon)": json.dumps(asdict(trajectory["endpoint"])),
                    "waypoints [(lat, lon)]": json.dumps([
                        asdict(waypoint)
                        for waypoint in trajectory["waypoints"]
                    ]),
                }
            )

        # Save generated virtual record
        virtualTrips.append(virtualTrip)

    # Create virtual dataset
    virtualDataset = pd.DataFrame(virtualTrips)

    # Save virtual dataset as CSV
    virtualDataset.to_csv(
        VIRTUAL_DATASETS / f"{generateVirtualDatasetId(sourceScenario)}.csv",
        index=False
    )

    return virtualDataset
