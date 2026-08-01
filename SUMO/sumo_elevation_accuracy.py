from data.validation.eVED_analysis import getElevationStats

from SUMO.sumo_utils import estimateSUMOElevationError

elevationStats = getElevationStats()

print("SUMO elevation error estimation: ")
print("Number of records:", len(elevationStats))

SUMOElevationError = estimateSUMOElevationError(
    elevationStats, len(elevationStats)
)

print("MAE:", SUMOElevationError["MAE"])
print("RMSE:", SUMOElevationError["RMSE"])
