import shutil
import os

import subprocess
import sys

import requests

from paths import VALIDATION_CONFIG, VALIDATION_CUSTOM, CONFIG, CUSTOM
from arguments import args

from pathlib import Path
from custom_types import GPSPoint

# Run duarouter using correct duarcfg file
def runDuarouter():
    customPath = VALIDATION_CUSTOM if args.validation else CUSTOM

    try:
        subprocess.run(
            [
                "duarouter",
                "--configuration-file",
                "custom.duarcfg",
                "--ignore-errors"
            ],
            cwd=customPath,
            check=True)
    except subprocess.CalledProcessError as duarError:
        print("DUAROUTER failed:", duarError)

# Run SUMO using correct sumocfg file
def runSUMO():
    configPath = VALIDATION_CONFIG if args.validation else CONFIG
    configFileName = "osm.sumocfg" if args.validation else "dataset.sumocfg"

    try:
        subprocess.run(
            [
                "sumo",
                "-c",
                configFileName
            ],
            cwd=configPath,
            check=True)
    except subprocess.CalledProcessError as sumoError:
        print("SUMO failed:", sumoError)

# This function generate a 3D SUMO net using a bindingbox specified by given GPSPoints
def generateSUMO3DNet(minGPSPoint: GPSPoint, maxGPSPoint: GPSPoint, datasetName: str = "dataset"):
    # Set SUMO_HOME path
    sumoHomePath = os.getenv("SUMO_HOME_PATH")

    if not sumoHomePath:
        raise RuntimeError("SUMO_HOME_PATH is not set in the environment")

    sumoHome = Path(sumoHomePath)

    # Dataset directory path
    datasetPath = CONFIG / datasetName

    # Remove dedicated dataset directory if it exists
    if datasetPath.exists():
        shutil.rmtree(datasetPath)

    # Create a dedicated directory for the dataset
    datasetPath.mkdir(parents=True)

    elevationFile = datasetPath / f"{datasetName}_elevation.tif"
    osmFile = datasetPath / f"{datasetName}_bbox.osm.xml"
    sumoNetFile = datasetPath / f"{datasetName}.net.xml"
    sumo3DNetFile = datasetPath / f"{datasetName}_3D.net.xml"

    try:
        # 1. Download elevation data
        downloadElevation(minGPSPoint, maxGPSPoint, elevationFile)

        if not elevationFile.exists():
            raise RuntimeError("Elevation file was not generated")

        # 2. Download OSM data
        subprocess.run(
            [
                sys.executable,
                str(sumoHome / "tools" / "osmGet.py"),
                (
                    f"--bbox="
                    f"{minGPSPoint.longitude},"
                    f"{minGPSPoint.latitude},"
                    f"{maxGPSPoint.longitude},"
                    f"{maxGPSPoint.latitude}"
                ),
                "--prefix",
                datasetName
            ],
            cwd=datasetPath,
            check=True
        )

        if not osmFile.exists():
            raise RuntimeError("OSM file was not generated")

        # 3. Build SUMO network from OSM
        subprocess.run(
            [
                sys.executable,
                str(sumoHome / "tools" / "osmBuild.py"),
                "--osm-file",
                osmFile.name,
                "--prefix",
                datasetName
            ],
            cwd=datasetPath,
            check=True
        )

        if not sumoNetFile.exists():
            raise RuntimeError("SUMO network was not generated")

        # Prepare environment for netconvert
        env = os.environ.copy()
        env["PATH"] = str(sumoHome / "bin") + os.pathsep + env["PATH"]

        # 4. Add elevation data to SUMO network
        subprocess.run(
            [
                str(sumoHome / "bin" / "netconvert.exe"),
                "--sumo-net-file",
                sumoNetFile.name,
                "--heightmap.geotiff",
                elevationFile.name,
                "--output-file",
                sumo3DNetFile.name
            ],
            cwd=datasetPath,
            env=env,
            check=True
        )

        if not sumo3DNetFile.exists():
            raise RuntimeError("3D SUMO network was not generated")

        print(f"SUMO 3D network generated: {sumo3DNetFile.name}")

    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"SUMO command failed with exit code "
            f"{error.returncode}"
        ) from error

# This functions calls an endpoint from OpenTopography API to download a .tif file within a bindingbox specified by given GPSPoints
# API Key is secret and provived using a .env file
def downloadElevation(minGPSPoint: GPSPoint, maxGPSPoint: GPSPoint, outputPath: Path):
    apiKey = os.getenv("OPENTOPOGRAPHY_API_KEY")
    margin = 0.01

    # Check if OpenTopography API Key is set
    if not apiKey:
        raise RuntimeError(
            "OPENTOPOGRAPHY_API_KEY is not set in the environment")

    # Send request to OpenTopography API
    response = requests.get(
        "https://portal.opentopography.org/API/globaldem",
        params={
            "demtype": "COP30",
            "south": minGPSPoint.latitude - margin,
            "north": maxGPSPoint.latitude + margin,
            "west": minGPSPoint.longitude - margin,
            "east": maxGPSPoint.longitude + margin,
            "outputFormat": "GTiff",
            "API_Key": apiKey
        }
    )

    response.raise_for_status()

    outputPath.write_bytes(response.content)
