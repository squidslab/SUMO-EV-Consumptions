import random

from custom_types import CustomVehicle

from SUMO.sumo_xml import buildCustomVehType

# Returns a map which associates every trajectory ID with its SUMO vehicle type
def mapSUMOVehicleTypes(otherIds: list[float], evedEVIds: list[float] = [], customType: CustomVehicle | None = None, randomize: bool = False):
    SUMOvehicleTypes: dict[float, str] = {}

    # eVED electric vehicles always use the Leaf 2013 vehicle type
    for trajectoryId in evedEVIds:
        SUMOvehicleTypes[trajectoryId] = "leaf_2013"

    # Define the vehicle types available for other trajectories
    EVTypes = [
        "tesla_model_y",
        "tesla_model_3",
        "chevrolet_equinox_ev",
        "ford_mustang_mach_e",
        "hyundai_ioniq_5"
    ]

    # Build the custom vehicle type if specified
    if customType is not None:
        buildCustomVehType(customType)

    # Randomly assign vehicle types while keeping their distribution balanced
    if randomize:
        vehicleTypes = EVTypes.copy()

        if customType is not None:
            vehicleTypes.append("custom_ev")

        # Create a balanced list of vehicle types to assign
        vehicleTypes = [
            vehicleTypes[i % len(vehicleTypes)]
            for i in range(len(otherIds))
        ]

        # Randomize the order while keeping the distribution balanced
        random.shuffle(vehicleTypes)

        for trajectoryId, vehicleType in zip(otherIds, vehicleTypes):
            SUMOvehicleTypes[trajectoryId] = vehicleType

    # Assign the same vehicle type to all other trajectories
    else:
        vehicleType = "custom_ev" if customType is not None else "ev_generic"

        for trajectoryId in otherIds:
            SUMOvehicleTypes[trajectoryId] = vehicleType

    return SUMOvehicleTypes
