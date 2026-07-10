from dataclasses import dataclass
import pandas as pd

@dataclass
class DatasetFile:
    name: str
    data: pd.DataFrame
