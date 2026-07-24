from datasets.dataset_analysis import getDatasetStats, getElevationStats

from SUMO.sumo_utils import estimateSUMOElevationError

datasetStats = getDatasetStats()
elevationStats = getElevationStats()

# Prints
print(datasetStats)

print("SUMO elevation error estimation: ")
print("Number of records:", len(elevationStats))

SUMOElevationError = estimateSUMOElevationError(
    elevationStats, len(elevationStats)
)

print("MAE:", SUMOElevationError["MAE"])
print("RMSE:", SUMOElevationError["RMSE"])
