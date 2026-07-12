from datasets.dataset_analysis import getTripStats
from SUMO.sumo import runSimulation

runSimulation(getTripStats())
