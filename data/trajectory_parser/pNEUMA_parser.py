import csv
import glob

from pathlib import Path
from custom_types import GPSPoint, TrajectorySample, Trajectory

from data.trajectory_parser.interface import TrajectoryParser

class pNEUMAParser(TrajectoryParser):

    def parse(self, path: Path) -> list[Trajectory]:
        # Rerieve dataset and build trajectories to return from it
        dataset = self.loadDataset(path)
        return self.buildTrajectories(dataset)

    def loadDataset(self, path: Path) -> list[list[str]]:
        csvFiles = glob.glob(str(path / "*.csv"))
        datasets: list[list[str]] = []

        for csvFile in csvFiles:
            # Extract the time interval (HHMM_HHMM) from the filename
            filename = Path(csvFile).stem
            timeInterval = "_".join(filename.split("_")[-2:])

            with open(csvFile, "r", encoding="utf-8") as file:
                reader = csv.reader(file, delimiter=";")

                # Skip the header
                next(reader)

                for row in reader:
                    if not row:
                        continue

                    # Make track ID unique across different files
                    row[0] = f"{timeInterval}_{row[0]}"

                    datasets.append(row)

        return datasets

    def buildTrajectories(self, dataset: list[list[str]]) -> list[Trajectory]:
        trajectories: list[Trajectory] = []

        # The first four columns contain trajectory metadata
        metadataColumns = 4

        # Each sample is represented by six columns: latitude, longitude, speed, longitudinal acceleration, lateral acceleration and timestamp
        sampleColumns = 6

        for row in dataset:
            trajectorySamples: list[TrajectorySample] = []

            # Skip the first four metadata columns and process the remaining columns in groups of six
            for start in range(metadataColumns, len(row), sampleColumns):
                sample = row[start:start + sampleColumns]

                # Ignore incomplete or invalid samples
                if (len(sample) < sampleColumns or any(value == "" for value in sample)):
                    continue

                trajectorySamples.append(
                    TrajectorySample(
                        point=GPSPoint(
                            latitude=float(sample[0]),
                            longitude=float(sample[1])
                        ),
                        timestamp=float(sample[5]) * 1000,
                        speed=float(sample[2]) / 3.6
                    )
                )

            if trajectorySamples:
                trajectories.append(
                    Trajectory(
                        trajectoryId=row[0],
                        samples=trajectorySamples
                    )
                )

        return trajectories
