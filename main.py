from paths import OUTPUT
from arguments import args

from data.validation.eVED_data import getElectricVehIds
from data.validation.eVED_analysis import getTripStats

from SUMO.sumo_utils import mapSUMOVehicleTypes
from SUMO.sumo import runSimulation

from virtual_data.dataset_generation import generateVirtualDataset

# Retrive data about trajectories from dataset
trajectories = getTripStats()

# Retrieve SUMO vehicle types map
SUMOvehicleTypes = mapSUMOVehicleTypes(
    evedEVIds=getElectricVehIds(types=["EV"]),
    otherIds=getElectricVehIds(types=["HEV", "PHEV"])
)

# Run SUMO simulation
runSimulation(trajectories, SUMOvehicleTypes, args.depart_delay)

# Generate virtual dataset using simulation results
generateVirtualDataset(OUTPUT / "tripinfos.xml", trajectories)

print("Virtual dataset generated!")
