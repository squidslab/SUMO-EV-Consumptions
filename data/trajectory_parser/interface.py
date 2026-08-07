from abc import ABC, abstractmethod
from pathlib import Path


from custom_types import Trajectory

class TrajectoryParser(ABC):
    """
    Abstract parser for datasets containing timestamped GPS trajectories.

    Every parser implementing this interface must convert its input dataset
    into a common trajectory representation.

    The output trajectory format is independent from the original dataset
    structure and contains an ordered collection of trajectory samples.
    Each sample contains a GPS position and may optionally include additional
    information available in the source dataset, such as timestamp, speed,
    or other movement-related attributes.
    """

    @abstractmethod
    def parse(self, path: Path) -> list[Trajectory]:
        """
        Reads a dataset and converts it into a collection of trajectories.

        Each trajectory contains:
            - trajectoryId: unique identifier of the trajectory
            - samples: ordered list of trajectory samples

        Each trajectory sample contains:
            - GPS coordinates
            - optional additional information provided by the dataset
              (e.g. timestamp, speed)

        Parameters
        ----------
        path : Path
            Path to the dataset.

        Returns
        -------
        list[Trajectory]
            Parsed trajectories using the common trajectory representation.
        """
        pass
