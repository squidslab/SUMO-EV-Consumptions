import subprocess

from SUMO.sumo_paths import CONFIG, CUSTOM

def runDuarouter():
    try:
        subprocess.run(
            [
                "duarouter",
                "--configuration-file",
                "custom.duarcfg",
                "--ignore-errors"
            ],
            cwd=CUSTOM,
            check=True)
    except subprocess.CalledProcessError as duarError:
        print("DUAROUTER failed:", duarError)

def runSUMO():
    try:
        subprocess.run(
            [
                "sumo",
                "-c",
                "osm.sumocfg"
            ],
            cwd=CONFIG,
            check=True)
    except subprocess.CalledProcessError as sumoError:
        print("SUMO failed:", sumoError)
