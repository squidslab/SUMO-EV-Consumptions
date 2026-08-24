import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--validation",
    action="store_true",
    help="Run SUMO validation - This config doesn't require a set database since it always uses eVED"
)

parser.add_argument(
    "--dataset",
    type=str,
    default=None,
    help="Trajectory dataset to use for the simulation"
)

parser.add_argument(
    "--skip-net-generation",
    action="store_false",
    dest="generate_net",
    default=True,
    help="Skip generation of a new 3D SUMO network"
)

parser.add_argument(
    "--skip-route-generation",
    action="store_false",
    dest="generate_ruotes",
    default=True,
    help="Skip generation of a new SUMO routes"
)

parser.add_argument(
    "--trajectory-batch",
    type=int,
    default=1,
    help="Trajectory batch to process (15,000 trajectories per batch)"
)

parser.add_argument(
    "--eved-veh-types",
    nargs="+",
    choices=["ICE", "HEV", "PHEV", "EV"],
    default=["HEV", "PHEV", "EV"],
    help="Vehicle types to include in the simulation when using eVED"
)

parser.add_argument(
    "--random-veh-types",
    action="store_true",
    help="Randomly assign SUMO electric vehicle types to trajectories with unknown vehicle models -"
    "By default, these trajectories are assigned to a generic electric vehicle type"
)

parser.add_argument(
    "--depart-delay",
    type=float,
    default=0,
    help="Delay between each simulated vehicle departure"
)

args = parser.parse_args()
