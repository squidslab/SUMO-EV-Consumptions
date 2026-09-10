import argparse

from custom_types import CustomVehicle

# Parses the custom vehicle string argument into an internal representation
def parseCustomVehicle(customVehicleArg: str) -> CustomVehicle:
    allowedParameters = {"mass", "accel", "max-speed", "battery"}

    parameters = {}

    for parameter in customVehicleArg.split(","):
        parameter = parameter.strip()

        # Must be a key=value pair
        if "=" not in parameter:
            raise argparse.ArgumentTypeError(
                f"invalid parameter '{parameter}', expected key=value"
            )

        key, parameterValue = parameter.split("=", 1)
        key = key.strip()
        parameterValue = parameterValue.strip()

        # Unknown parameter
        if key not in allowedParameters:
            raise argparse.ArgumentTypeError(
                f"unknown parameter '{key}'"
            )

        # Value must be numeric
        try:
            parameters[key] = float(parameterValue)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"invalid value for '{key}': '{parameterValue}'"
            )

    return CustomVehicle(
        mass=parameters.get("mass"),
        accel=parameters.get("accel"),
        maxSpeed=parameters.get("max-speed"),
        battery=parameters.get("battery")
    )


parser = argparse.ArgumentParser()

# Main arguments
parser.add_argument(
    "--validation",
    action="store_true",
    help="Run SUMO validation. "
         "This config doesn't require a set database since it always uses eVED."
)

parser.add_argument(
    "--scenario",
    type=str,
    choices=["dataset", "city"],
    default="dataset",
    help="Specify the simulation scenario type: 'dataset' for a trajectory dataset or 'city' for a city."
)

parser.add_argument(
    "--scenario-name",
    type=str,
    default="eVED",
    help="Name of the simulation scenario: a trajectory dataset or a city. "
         "For cities, it is recommended to use the format 'Naples, Italy'. "
         "When a city is specified, random trajectories are generated within its area."
)

# Skip arguments
parser.add_argument(
    "--skip-net-generation",
    action="store_false",
    dest="generate_net",
    default=True,
    help="Skip generation of a new 3D SUMO network."
)

parser.add_argument(
    "--skip-route-generation",
    action="store_false",
    dest="generate_ruotes",
    default=True,
    help="Skip generation of a new SUMO routes."
)

# Scenario-specific arguments
parser.add_argument(
    "--trajectory-batch",
    type=int,
    default=1,
    help="Batch of trajectories to process (15,000 trajectories per batch). "
         "Only applicable to the 'dataset' scenario."
)

parser.add_argument(
    "--trajectories-number",
    type=int,
    default=5000,
    help="Number of random trajectories to generate. "
         "Only applicable to the 'city' scenario."
)

# Vehicle types arguments
parser.add_argument(
    "--eved-veh-types",
    nargs="+",
    choices=["ICE", "HEV", "PHEV", "EV"],
    default=["HEV", "PHEV", "EV"],
    metavar="TYPE",
    help="Vehicle types to include in the simulation when using eVED."
)

parser.add_argument(
    "--random-veh-types",
    action="store_true",
    help="Randomly assign an electric vehicle type to trajectories "
         "with unknown vehicle models. When not specified, the default "
         "generic electric vehicle is used, unless --custom-vehicle "
         "is specified. If --custom-vehicle is also specified, the "
         "custom vehicle is included in the randomization pool."
)

parser.add_argument(
    "--custom-vehicle",
    type=parseCustomVehicle,
    metavar="PARAMETERS",
    default=None,
    help="Specify a custom electric vehicle using the format: "
         "'mass=1800,accel=2.5,max-speed=160,battery=75'. "
         "Mass is expressed in kg, acceleration in m/s², "
         "maximum speed in km/h and battery capacity in kWh. "
         "When specified without --random-veh-types, it is used "
         "instead of the default generic electric vehicle. "
         "When used with --random-veh-types, it is added to the "
         "randomization pool."
)

# Depart delay argument
parser.add_argument(
    "--depart-delay",
    type=float,
    default=0,
    help="Delay between each simulated vehicle departure."
)

args = parser.parse_args()
