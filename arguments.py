import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--vehicle-types",
    nargs="+",
    choices=["HEV", "PHEV", "EV"],
    default=["HEV", "PHEV", "EV"],
    help="Vehicle types to include in the simulation"
)

args = parser.parse_args()
