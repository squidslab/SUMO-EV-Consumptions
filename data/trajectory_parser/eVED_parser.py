import glob
import pandas as pd
import os

from pathlib import Path
from custom_types import GPSPoint, TrajectorySample, Trajectory

from data.trajectory_parser.interface import TrajectoryParser

class EVEDParser(TrajectoryParser):

    def __init__(self, staticPath: Path, vehicleTypes: list[str] = ["ICE", "HEV", "PHEV", "EV"]):
        self.staticPath = staticPath
        self.vehicleTypes = vehicleTypes

    def parse(self, path: Path) -> list[Trajectory]:
        # Rerieve dataset and vehicles ids for requested types
        dataset = self.loadDataset(path)
        vehIds = self.getVehicleIds()

        # Select only vehicles for requested types from dataset then sort it to order data correctly
        dataset = dataset[dataset["VehId"].isin(vehIds)]
        dataset = dataset.sort_values(
            ["DayNum", "VehId", "Trip", "Timestamp(ms)"]
        )

        # Build trajectories from dataset then return them
        return self.buildTrajectories(dataset)

    def loadDataset(self, path: Path) -> pd.DataFrame:
        csvFiles = glob.glob(str(path / "*.csv"))
        datasets = []

        for csv in csvFiles:
            datasets.append(
                pd.read_csv(csv, dtype={"Speed Limit[km/h]": str})
            )

        return pd.concat(datasets, ignore_index=True)

    def getVehicleIds(self) -> list[float]:
        csvFiles = glob.glob(str(self.staticPath / "*.csv"))
        vehIds = []

        for csv in csvFiles:
            dataframe = pd.read_csv(csv)
            filename = os.path.splitext(os.path.basename(csv))[0]

            match filename:
                case "VED_Static_Data_ICE&HEV":
                    if "ICE" in self.vehicleTypes:
                        vehIds.extend(
                            dataframe.loc[
                                dataframe["Vehicle Type"] == "ICE", "VehId"
                            ].tolist()
                        )

                    if "HEV" in self.vehicleTypes:
                        vehIds.extend(
                            dataframe.loc[
                                dataframe["Vehicle Type"] == "HEV", "VehId"
                            ].tolist()
                        )

                case "VED_Static_Data_PHEV&EV":
                    if "PHEV" in self.vehicleTypes:
                        vehIds.extend(
                            dataframe.loc[
                                dataframe["EngineType"] == "PHEV", "VehId"
                            ].tolist()
                        )

                    if "EV" in self.vehicleTypes:
                        vehIds.extend(
                            dataframe.loc[
                                dataframe["EngineType"] == "EV", "VehId"
                            ].tolist()
                        )

        return vehIds

    def buildTrajectories(self, dataset: pd.DataFrame) -> list[Trajectory]:
        trajectories: list[Trajectory] = []

        for (vehId, tripId), trip in dataset.groupby(["VehId", "Trip"]):
            trajectorySamples = [
                TrajectorySample(
                    point=GPSPoint(
                        latitude=float(row["Matchted Latitude[deg]"]),
                        longitude=float(row["Matched Longitude[deg]"])
                    ),
                    timestamp=float(row["Timestamp(ms)"]),
                    speed=float(row["Vehicle Speed[km/h]"] / 3.6)
                )
                for _, row in trip.iterrows()
            ]

            trajectories.append(
                Trajectory(
                    trajectoryId=f"{vehId}_{tripId}",
                    samples=trajectorySamples
                )
            )

        return trajectories
