from pathlib import Path

ROOT = Path(__file__).parent

DATA = ROOT / "data"
DATASETS = ROOT / "datasets"
SUMO = ROOT / "SUMO"
VIRTUAL_DATA = ROOT / "virtual_data"
VIRTUAL_DATASETS = ROOT / "virtual_datasets"

EVED = DATASETS / "eVED"
EVED_STATIC = EVED / "static"

DLR = DATASETS / "DLR_UT"

PNEUMA = DATASETS / "pNEUMA"

SUMO_FILES = SUMO / "sumo_files"
SUMO_FILES_VALIDATION = SUMO / "sumo_files_validation"

CONFIG = SUMO_FILES / "config"
CUSTOM = SUMO_FILES / "custom"
OUTPUT = SUMO_FILES / "output"

VALIDATION_CONFIG = SUMO_FILES_VALIDATION / "config"
VALIDATION_CUSTOM = SUMO_FILES_VALIDATION / "custom"
VALIDATION_OUTPUT = SUMO_FILES_VALIDATION / "output"
