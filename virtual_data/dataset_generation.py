import re
import math
import json
from datetime import datetime

import xml.etree.ElementTree as ET
import pandas as pd

from pathlib import Path
from paths import VIRTUAL_DATASETS

def generateVirtualDatasetId():
    # Get current date in YYYYMMDD format
    date = datetime.now().strftime("%Y%m%d")

    # Search for existing datasets generated today
    pattern = re.compile(rf"{date}_(\d{{3}})\.csv")

    simulationNumbers = []
    for dataset in VIRTUAL_DATASETS.glob(f"{date}_*.csv"):
        match = pattern.match(dataset.name)

        if match:
            simulationNumbers.append(int(match.group(1)))

    # Generate the next progressive number
    nextNumber = max(simulationNumbers, default=0) + 1

    return f"{date}_{nextNumber:03d}"

# Generates a virtual dataset from SUMO tripinfo.xml obtained from a simulation
def generateVirtualDataset(tripInfosPath: Path, trajectories: pd.DataFrame):
    # Parse SUMO tripinfos.xml at given path
    tripInfosXml = ET.parse(tripInfosPath)
    tripInfos = tripInfosXml.getroot()

    # Create a dictionary using trajectoryId and retrieve the original trajectory metadata using the same id found in tripinfos.xml
    trajectoryMetadata = {
        trajectory['trajectoryId']: trajectory
        for trajectory in trajectories.to_dict(orient="records")
    }

    virtualTrips = []

    # Extract data for each simulated trip
    for tripInfo in tripInfos.findall("tripinfo"):
        trajectoryId = tripInfo.get("id")

        # Retrieve original trajectory metadata
        trajectory = trajectoryMetadata.get(trajectoryId)

        # Skip trips for which the original trajectory metadata cannot be found
        if trajectory is None:
            continue

        # Retrieve battery info
        battery = tripInfo.find("battery")

        # Skip trips without battery information
        if battery is None:
            continue

        virtualTrips.append({
            "trajectoryId": trajectoryId,
            "vehicleType": tripInfo.get("vType"),

            "tripDuration (s)": float(tripInfo.get("duration", 0.0)),
            "tripDistance (m)": float(tripInfo.get("routeLength", 0.0)),
            "tripAvgSpeed (m/s)": math.ceil(float(tripInfo.get("routeLength")) / float(tripInfo.get("duration")) * 100) / 100,

            "sourceDataset": "eVED",
            "startpoint (lat, lon)": json.dumps(trajectory["startpoint"]),
            "endpoint (lat, lon)": json.dumps(trajectory["endpoint"]),
            "waypoints [(lat, lon)]": json.dumps(trajectory["waypoints"]),

            "batteryCapacity (Wh)": float(battery.get("actualBatteryCapacity", 0.0)),
            "energyConsumed (Wh)": float(battery.get("totalEnergyConsumed", 0.0)),
            "energyRegenerated (Wh)": float(battery.get("totalEnergyRegenerated", 0.0)),
        })

    # Create virtual dataset
    virtualDataset = pd.DataFrame(virtualTrips)

    # Save virtual dataset as CSV
    virtualDataset.to_csv(
        VIRTUAL_DATASETS / f"{generateVirtualDatasetId()}.csv",
        index=False
    )

    return virtualDataset
