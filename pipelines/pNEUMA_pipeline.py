from paths import PNEUMA, OUTPUT
from arguments import args

from data.utils import getTrajectoriesBounds, getTrajectoryBatch, buildTrajectoryDataframe
from data.trajectory_parser.pNEUMA_parser import pNEUMAParser

from SUMO.sumo_processes import generateSUMO3DNet
from SUMO.sumo import runSimulation

from virtual_data.simulation_results import printSimulationStats
from virtual_data.dataset_generation import generateVirtualDataset

def runPNEUMAPipeline():
    # Initialize pNEUMA parser
    parser = pNEUMAParser()

    # Retrieve data about trajectories from pNEUMA
    pNEUMATrajectories = parser.parse(PNEUMA)

    # Generate SUMO 3D Net using dataset bounds obtained via trajectories data if requested
    if args.generate_net:
        minGPSPoint, maxGPSPoint = getTrajectoriesBounds(pNEUMATrajectories)
        generateSUMO3DNet(minGPSPoint, maxGPSPoint, args.dataset)

    # Retrieve trajectory batch to process (15,000 trajectories per batch)
    trajectories = getTrajectoryBatch(
        pNEUMATrajectories, args.trajectory_batch
    )

    # Log trajectory batch info
    print(
        f"Processing trajectory batch {args.trajectory_batch}: "
        f"{len(trajectories)} trajectories"
    )

    # Build trajectory as dataframe so it is suitable for SUMO simulation function
    SUMOtrajectories = buildTrajectoryDataframe(trajectories, True)

    # Run SUMO simulation
    _, SUMOSimStats = runSimulation(SUMOtrajectories, args.depart_delay)

    # Log simulation stats
    printSimulationStats(SUMOSimStats)

    # Generate virtual dataset using simulation results
    generateVirtualDataset(
        OUTPUT / args.dataset,
        SUMOtrajectories,
        args.dataset
    )
