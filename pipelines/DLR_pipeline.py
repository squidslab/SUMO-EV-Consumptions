from paths import DLR, OUTPUT
from arguments import args

from data.utils import getTrajectoriesBounds, getTrajectoryBatch, buildTrajectoryDataframe
from data.trajectory_parser.DLR_parser import DLRParser

from SUMO.sumo_processes import generateSUMO3DNet
from SUMO.sumo_utils import mapSUMOVehicleTypes
from SUMO.sumo import runSimulation

from virtual_data.simulation_results import printSimulationStats
from virtual_data.dataset_generation import generateVirtualDataset

def runDLRPipeline():
    # Initialize DLR parser
    parser = DLRParser()

    # Retrieve data about trajectories from DLR
    DLRTrajectories = parser.parse(DLR)

    # Generate SUMO 3D Net using dataset bounds obtained via trajectories data if requested
    if args.generate_net:
        minGPSPoint, maxGPSPoint = getTrajectoriesBounds(DLRTrajectories)
        generateSUMO3DNet(minGPSPoint, maxGPSPoint, args.dataset)

    # Retrieve trajectory batch to process (15,000 trajectories per batch)
    trajectories = getTrajectoryBatch(DLRTrajectories, args.trajectory_batch)

    # Log trajectory batch info
    print(
        f"Processing trajectory batch {args.trajectory_batch}: "
        f"{len(trajectories)} trajectories"
    )

    # Build trajectory as dataframe so it is suitable for SUMO simulation function
    SUMOtrajectories = buildTrajectoryDataframe(trajectories, True)

    # Retrieve trajectory ids for each trajectory
    trajectoryIds = SUMOtrajectories["trajectoryId"].unique().tolist()

    # Retrieve SUMO vehicle types map
    SUMOvehicleTypes = mapSUMOVehicleTypes(
        trajectoryIds, randomize=args.random_veh_types
    )

    # Run SUMO simulation
    _, SUMOSimStats = runSimulation(
        SUMOtrajectories, args.depart_delay, SUMOvehicleTypes
    )

    # Log simulation stats
    printSimulationStats(SUMOSimStats)

    # Generate virtual dataset using simulation results
    generateVirtualDataset(
        OUTPUT / args.dataset,
        SUMOtrajectories,
        args.dataset
    )
