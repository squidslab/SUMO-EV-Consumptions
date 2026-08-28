from data.validation.eVED_analysis import loadEVED, getElevationStats

from SUMO.sumo_utils import loadSUMONetwork, estimateSUMOElevationError

loadEVED()

elevationStats = getElevationStats()

loadSUMONetwork()

print("SUMO elevation error estimation: ")
print("Number of records:", len(elevationStats))

SUMOElevationError = estimateSUMOElevationError(
    elevationStats, len(elevationStats)
)

print("MAE:", SUMOElevationError["MAE"])
print("RMSE:", SUMOElevationError["RMSE"])
