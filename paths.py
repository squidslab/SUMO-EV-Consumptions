from pathlib import Path

ROOT = Path(__file__).parent

DATA = ROOT / "data"
DATASETS = ROOT / "datasets"
SUMO = ROOT / "SUMO"
VIRTUAL_DATA = ROOT / "virtual_data"
VIRTUAL_DATASETS = ROOT / "virtual_datasets"

EVED = DATASETS / "eVED"
EVED_STATIC = EVED / "static"

CONFIG = SUMO / "config"
CUSTOM = SUMO / "custom"
OUTPUT = SUMO / "output"
