import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--eved-veh-types",
    nargs="+",
    choices=["HEV", "PHEV", "EV"],
    default=["HEV", "PHEV", "EV"],
    help="Vehicle types to include in the simulation when using eVED"
)

parser.add_argument(
    "--depart-delay",
    type=float,
    default=None,
    help="Delay between each vehicle departure"
)

args = parser.parse_args()
