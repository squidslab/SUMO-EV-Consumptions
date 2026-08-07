import os
import glob
import pandas as pd

from paths import EVED, EVED_STATIC
from custom_types import DatasetFile

eVEDPath = str(EVED)
eVEDStaticPath = str(EVED_STATIC)

# Returns eVED using csv files. It can be returned as a whole dataframe or a list of dataframes for each csv file.
def getDataset(entire: bool = True):
    csvFiles = glob.glob(eVEDPath + "/*.csv")
    datasetFiles: list[DatasetFile] = []

    # Read csv files, create a dataframe for each then append them in the datasetFiles list
    for csv in csvFiles:
        dataframe = pd.read_csv(csv, dtype={'Speed Limit[km/h]': str})
        datasetFiles.append(
            DatasetFile(
                name=os.path.splitext(os.path.basename(csv))[0],
                data=dataframe
            )
        )

    # Return the entire dataset or a list contaning a dataframe for each csv
    if (entire):
        return pd.concat(
            list(map(lambda datasetFile: datasetFile.data, datasetFiles)),
            ignore_index=True
        )
    else:
        return datasetFiles

# Returns vehicle ids for HEV, PHEV and/or EV vehicles
def getElectricVehIds(types: list[str] = ["HEV", "PHEV", "EV"]):
    csvFiles = glob.glob(eVEDStaticPath + "/*.csv")
    electricVehIds: list[float] = []

    # Based on filename, read csv files and extract needed vehIds
    for csv in csvFiles:
        dataframe = pd.read_csv(csv)
        staticFileName = os.path.splitext(os.path.basename(csv))[0]

        match staticFileName:
            case "VED_Static_Data_ICE&HEV":
                if ("HEV" in types):
                    electricVehIds.extend(
                        dataframe.loc[
                            dataframe["Vehicle Type"] == "HEV", "VehId"
                        ].tolist()
                    )

            case "VED_Static_Data_PHEV&EV":
                if ("PHEV" in types):
                    electricVehIds.extend(
                        dataframe.loc[
                            dataframe["EngineType"] == "PHEV", "VehId"
                        ].tolist()
                    )

                if ("EV" in types):
                    electricVehIds.extend(
                        dataframe.loc[
                            dataframe["EngineType"] == "EV", "VehId"
                        ].tolist()
                    )

    return electricVehIds

# Returns dataset containing only electric vehicles (HEV, PHEV and/or EV) from eVED
def getDatasetEV(include: list[str] = ["HEV", "PHEV", "EV"], entire: bool = True):
    dataset = getDataset(entire)
    electricVehIds: list[float] = getElectricVehIds(types=include)

    if (entire):
        return dataset[dataset["VehId"].isin(electricVehIds)]
    else:
        return list(
            map(
                lambda datasetFile: DatasetFile(
                    name=datasetFile.name,
                    data=datasetFile.data[datasetFile.data["VehId"].isin(
                        electricVehIds)]
                ),
                dataset
            )
        )
