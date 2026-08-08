from paths import EVED, EVED_STATIC, OUTPUT
from arguments import args

from data.utils import buildTrajectoryDataframe
from data.trajectory_parser.eved_parser import EVEDParser

from SUMO.sumo_utils import mapSUMOVehicleTypes
from SUMO.sumo import runSimulation

from virtual_data.dataset_generation import generateVirtualDataset

# Initialize dataset parser
parser = EVEDParser(staticPath=EVED_STATIC, vehicleTypes=args.eved_veh_types)

# Retrieve data about trajectories from dataset at given path by parsing it using initialized parser
trajectories = parser.parse(EVED)

# Build trajectory as dataframe so it is suitable for SUMO simulation function
SUMOtrajectories = buildTrajectoryDataframe(trajectories, True)

# Run SUMO simulation
runSimulation(SUMOtrajectories, args.depart_delay)

# Generate virtual dataset using simulation results
generateVirtualDataset(OUTPUT / "tripinfos.xml", SUMOtrajectories)

# Print
print("Virtual dataset generated!")
