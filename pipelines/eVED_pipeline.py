from paths import EVED, EVED_STATIC, OUTPUT
from arguments import args

from data.utils import getTrajectoriesBounds, buildTrajectoryDataframe
from data.trajectory_parser.eVED_parser import EVEDParser

from SUMO.sumo_processes import generateSUMO3DNet
from SUMO.sumo import runSimulation

from virtual_data.dataset_generation import generateVirtualDataset

def runEVEDPipeline():
    # Initialize eVED parser
    parser = EVEDParser(
        staticPath=EVED_STATIC,
        vehicleTypes=args.eved_veh_types
    )

    # Retrieve data about trajectories from eVED
    trajectories = parser.parse(EVED)

    # Generate SUMO 3D Net using dataset bounds obtained via trajectories data
    if args.generate_net:
        minGPSPoint, maxGPSPoint = getTrajectoriesBounds(trajectories)
        generateSUMO3DNet(minGPSPoint, maxGPSPoint, args.dataset)

    # Build trajectories as dataframe so it is suitable for SUMO simulation function
    SUMOtrajectories = buildTrajectoryDataframe(trajectories, True)

    # Run SUMO simulation
    runSimulation(SUMOtrajectories, args.depart_delay)

    # Generate virtual dataset using simulation results
    generateVirtualDataset(
        OUTPUT / args.dataset,
        SUMOtrajectories,
        args.dataset
    )
