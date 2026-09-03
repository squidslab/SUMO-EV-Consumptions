from abc import ABC, abstractmethod
import pandas as pd

from pathlib import Path
from custom_types import Trajectory

class TrajectoryParser(ABC):
    """
    Abstract parser for datasets containing trajectories.

    Every parser implementing this interface must:
        1. Load its source dataset into a DataFrame.
        2. Convert the DataFrame into the common Trajectory representation.

    The output trajectory format is independent from the original dataset
    structure and contains an ordered collection of trajectory samples.
    """

    def parse(self, path: Path) -> list[Trajectory]:
        """
        Loads a dataset and converts it into the common trajectory format.

        This method defines the common parsing flow shared by all parsers.
        Dataset-specific loading and trajectory construction are delegated
        to the corresponding abstract methods.
        """
        dataset = self.loadDataset(path)
        return self.buildTrajectories(dataset)

    @abstractmethod
    def loadDataset(self, path: Path) -> pd.DataFrame:
        """
        Loads the source dataset into a DataFrame.

        The implementation is responsible for handling the specific
        file format and structure of the dataset.

        Parameters
        ----------
        path : Path
            Path to the dataset.

        Returns
        -------
        pd.DataFrame
            Raw or preprocessed dataset.
        """
        pass

    @abstractmethod
    def buildTrajectories(self, dataset: pd.DataFrame) -> list[Trajectory]:
        """
        Converts the loaded dataset into the common trajectory format.

        The implementation is responsible for interpreting the dataset
        columns and constructing ordered Trajectory objects.

        Parameters
        ----------
        dataset : pd.DataFrame
            Dataset returned by loadDataset().

        Returns
        -------
        list[Trajectory]
            Parsed trajectories using the common trajectory representation.
        """
        pass
