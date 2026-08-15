import glob
import pandas as pd
from pyproj import Transformer

from pathlib import Path
from custom_types import GPSPoint, TrajectorySample, Trajectory

from data.trajectory_parser.interface import TrajectoryParser

class DLRParser(TrajectoryParser):

    def __init__(self):
        self.transformer = Transformer.from_crs(
            "EPSG:32632",
            "EPSG:4326",
            always_xy=True
        )

    def parse(self, path: Path) -> list[Trajectory]:
        # Rerieve dataset
        dataset = self.loadDataset(path).sort_values(["timestamp", "id"])

        # Convert all UTM coordinates to WGS84 at once
        longitudes, latitudes = self.transformer.transform(
            dataset["center_easting"].to_numpy(),
            dataset["center_northing"].to_numpy()
        )

        # Store converted coordinates in the dataset
        dataset["longitude"] = longitudes
        dataset["latitude"] = latitudes

        # Build trajectories from it then return them
        return self.buildTrajectories(dataset)

    def loadDataset(self, path: Path) -> pd.DataFrame:
        csvFiles = glob.glob(str(path / "*.csv"))
        datasets = []

        for csv in csvFiles:
            datasets.append(pd.read_csv(csv, parse_dates=["timestamp"]))

        return pd.concat(datasets, ignore_index=True)

    def buildTrajectories(self, dataset: pd.DataFrame) -> list[Trajectory]:
        trajectories: list[Trajectory] = []

        for trajectoryId, trajectory in dataset.groupby("id"):
            trajectorySamples: list[TrajectorySample] = []

            startTimestamp = trajectory["timestamp"].iloc[0]

            for _, row in trajectory.iterrows():
                timestamp = (
                    row["timestamp"] - startTimestamp
                ).total_seconds() * 1000

                trajectorySamples.append(
                    TrajectorySample(
                        point=GPSPoint(
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"])
                        ),
                        timestamp=timestamp,
                        speed=float(
                            row["velocity_magnitude"]
                        )
                    )
                )

            trajectories.append(
                Trajectory(
                    trajectoryId=str(trajectoryId),
                    samples=trajectorySamples
                )
            )

        return trajectories
