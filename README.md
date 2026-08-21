# SUMO-EV-Consumption

**SUMO-EV-Consumption** is a tool for generating virtual electric-vehicle consumptions datasets using [SUMO (Simulation of Urban MObility)](https://www.eclipse.org/sumo/).

The tool accepts trajectory datasets, converts them into a common internal representation, generates a suitable 3D SUMO network, performs the simulation and produces a virtual dataset based on the simulation results.

---

## Requirements

Before running the tool, make sure the following are installed:

* Python
* SUMO
* The Python dependencies listed below

SUMO must be installed locally because the tool uses several SUMO utilities, including:

* `osmGet`
* `osmBuild`
* `netconvert`
* `duarouter`
* `sumo`

### Python dependencies

The project currently uses the following external Python modules/libraries:

```text
pyproj
pandas
matplotlib
rtree
python-dotenv
requests
```

The modules are used for different aspects of the tool, including:

* **pyproj** — coordinate system transformations.
* **pandas** — loading and processing trajectory datasets.
* **matplotlib** — plotting and visualizing validation results.
* **rtree** — spatial indexing and geographical queries.
* **python-dotenv** — loading configuration variables from the `.env` file.
* **requests** — communicating with external APIs, including OpenTopography.

---

## Environment configuration

The tool uses a `.env` file to store environment-specific configuration.

Create a `.env` file in the root directory of the project:

```text
SUMO_HOME_PATH="C:\path\to\sumo"
OPENTOPOGRAPHY_API_KEY="your_api_key"
```

### `SUMO_HOME_PATH`

`SUMO_HOME_PATH` specifies the location of the SUMO installation that should be used by the tool.

For example:

```text
SUMO_HOME_PATH="C:\Program Files (x86)\Eclipse\Sumo"
```

The path is used to locate SUMO executables and Python tools such as:

* `netconvert.exe`
* `sumo.exe`
* `osmGet.py`
* `osmBuild.py`

Using this variable instead of relying directly on the system `SUMO_HOME` variable allows each user to specify which SUMO installation should be used by the tool.

### `OPENTOPOGRAPHY_API_KEY`

`OPENTOPOGRAPHY_API_KEY` is the API key used to access the [OpenTopography](https://opentopography.org/) API.

The tool uses OpenTopography to automatically download elevation data covering the geographical area of the trajectory dataset. This elevation data is subsequently used by `netconvert` to generate a 3D SUMO network.

The API key should be kept private and must **not** be committed to the repository.

The `.env` file is therefore included in `.gitignore`.

---

# Adding a new trajectory dataset

The tool is designed to support multiple trajectory datasets through a common parser interface and dataset-specific pipelines.

To integrate a new dataset from scratch, three main steps are required:

1. Implement the trajectory parser.
2. Create a pipeline for the dataset.
3. Register the pipeline in `main.py`.

---

## 1. Implement the trajectory parser

Every trajectory dataset must be converted into the common trajectory representation used by the tool.

The abstract parser interface is located at:

```text
data/
└── trajectory_parser/
    └── interface.py
```

The interface defines the methods that every dataset-specific parser must implement.

Create a new Python file inside `data/trajectory_parser/` for the dataset.

For example:

```text
data/
└── trajectory_parser/
    ├── interface.py
    ├── eved_parser.py
    └── my_dataset_parser.py
```

The new parser must inherit from `TrajectoryParser`:

```python
from pathlib import Path

from data.trajectory_parser.interface import TrajectoryParser
from custom_types import Trajectory

class MyDatasetParser(TrajectoryParser):

    def parse(self, path: Path) -> list[Trajectory]:
        ...
```

The parser is responsible for converting the original dataset format into the common representation:

```python
@dataclass
class Trajectory:
    trajectoryId: str
    samples: list[TrajectorySample]

@dataclass
class TrajectorySample:
    point: GPSPoint
    timestamp: float | None = None
    speed: float | None = None

@dataclass
class GPSPoint:
    latitude: float
    longitude: float
```

The implementation can contain dataset-specific logic such as:

* Loading CSV or other source files.
* Filtering trajectories or vehicles.
* Converting coordinate systems.
* Converting timestamps.
* Extracting speed.
* Ordering trajectory samples.
* Grouping samples into trajectories.

A parser should expose the dataset through the common `Trajectory` representation regardless of how the original dataset is structured.

### Recommended parser structure

When appropriate, the parser can be organized into separate methods for loading the original dataset and converting it into trajectories:

```python
class MyDatasetParser(TrajectoryParser):

    def parse(self, path: Path) -> list[Trajectory]:
        dataset = self.loadDataset(path)

        # Dataset-specific preprocessing

        return self.buildTrajectories(dataset)

    def loadDataset(self, path: Path):
        ...

    def buildTrajectories(self, dataset) -> list[Trajectory]:
        ...
```

The exact implementation depends on the structure of the dataset.

---

# 2. Create a dataset-specific pipeline

Once the parser has been implemented, create a pipeline for the new dataset inside:

```text
pipelines/
```

For example:

```text
pipelines/
├── eVED_pipeline.py
├── DLR_pipeline.py
└── my_dataset_pipeline.py
```

The pipeline is responsible for orchestrating the operations required for that dataset.

A typical pipeline performs the following operations:

1. Initialize the dataset parser.
2. Parse the dataset.
3. Determine the geographical bounds of the trajectories.
4. Generate the SUMO 3D network if required.
5. Convert trajectories into SUMO-compatible trips.
6. Run the SUMO simulation, including SUMO route generation if required.
7. Generate the resulting virtual dataset.

Dataset-specific operations should remain inside the dataset's pipeline rather than being added to the generic parser.

---

# 3. Add the pipeline to `main.py`

Finally, the new pipeline must be made available from `main.py`.

The selected dataset is determined using the `--dataset` argument.

The main program should therefore dispatch execution to the appropriate pipeline depending on the selected dataset.

For example:

```python
match args.dataset:
    case "eVED":
        runEVEDPipeline(...)
    case "pNEUMA":
        runPNEUMAPipeline()
```

When adding a new dataset, remember to:

* Import its pipeline.
* Add the corresponding pipeline invocation to `main.py`.
* Add the dataset files under the appropriate directory in `datasets/`.

---

# Command-line arguments

The tool can be configured through command-line arguments.

## `--validation`

Runs the SUMO validation workflow.

```bash
python main.py --validation
```

This mode is intended to validate the reliability of the SUMO simulation, by comparing the simulated trajectories with the original reference trajectories and calculating the corresponding errors regarding energy consumptions.

**Important:** `--validation` is currently only supported for **eVED**.

The required eVED dataset must therefore be correctly placed inside:

```text
datasets/eVED/
```

before using this option.

---

## `--dataset`

Specifies which trajectory dataset should be used.

```bash
python main.py --dataset eVED
```

The value must correspond to a dataset supported by the tool and implemented in `pipelines/`.

For example:

```bash
python main.py --dataset eVED
```

or:

```bash
python main.py --dataset pNEUMA
```

depending on the datasets currently integrated into the project.

---

## `--skip-net-generation`

Skips the automatic generation of the 3D SUMO network.

```bash
python main.py --dataset eVED --skip-net-generation
```

This is useful when a suitable network has already been generated and should be reused instead of downloading OSM and elevation data and rebuilding the network.

---

## `--skip-route-generation`

Skips the generation of SUMO routes.

```bash
python main.py --dataset eVED --skip-route-generation
```

This option is useful when routes have already been generated and should be reused.

`--skip-route-generation` should **not** be used by itself, since routes normally depend on the network generated or selected for the current execution.

The route and network generation flags can otherwise be combined as needed:

```text
--skip-net-generation
--skip-route-generation
```

or:

```bash
python main.py --dataset eVED --skip-net-generation --skip-route-generation
```

---

## `--trajectory-batch`

Specifies which batch of trajectories should be processed.

The tool processes trajectories in batches of **15,000 trajectories** by default. This allows large trajectory datasets to be processed through multiple executions, keeping individual simulation times more manageable.

The argument specifies the batch number:

* `1` — first 15,000 trajectories
* `2` — trajectories 15,001–30,000
* `3` — trajectories 30,001–45,000
* and so on.

For example:

```bash
python main.py --dataset eVED --trajectory-batch 2
```

This processes the second batch of 15,000 trajectories.
The default value is `1`, meaning that the first batch is processed when no value is explicitly specified.
If the selected batch contains fewer than 15,000 remaining trajectories, all remaining trajectories are processed.
This option is particularly useful for generating a virtual dataset in multiple smaller executions, which can subsequently be combined into a larger dataset.

---

## `--eved-veh-types`

Specifies which vehicle types should be extracted when running the eVED pipeline or in validation mode.

The supported vehicle types are:

* `ICE` — Internal Combustion Engine
* `HEV` — Hybrid Electric Vehicle
* `PHEV` — Plug-in Hybrid Electric Vehicle
* `EV` — Electric Vehicle

When running in validation mode, the ICE vehicle type is ignored even if specified, since validation is only supported for HEV, PHEV, and EV vehicles.
Using EV is recommended for validation, as it provides the most direct comparison for electric-vehicle consumption.

For example, to process only electric vehicles:

```bash
python main.py --dataset eVED --eved-veh-types EV
```

Multiple types can be specified:

```bash
python main.py --dataset eVED --eved-veh-types EV HEV PHEV
```

For example, to include all supported vehicle types:

```bash
python main.py --dataset eVED --eved-veh-types ICE HEV PHEV EV
```

This option only applies to the eVED dataset.

---

## `--depart-delay`

Specifies the delay in seconds between the departure times of generated SUMO trips.

For example:

```bash
python main.py --dataset eVED --depart-delay 10
```

The shortest execution time is achieved by setting this argument to `0`, which is also the default value.
Collisions are disabled by default for all SUMO simulations, ensuring that vehicles do not interact with or influence each other's behavior.

---

# Example workflows

### Run a dataset normally

```bash
python main.py --dataset eVED
```

This performs the complete pipeline, including network and route generation.

### Reuse an existing network

```bash
python main.py --dataset eVED --skip-net-generation
```

### Reuse both network and routes

```bash
python main.py --dataset eVED --skip-net-generation --skip-route-generation
```

### Process a specific trajectory batch

```bash
python main.py --dataset eVED --trajectory-batch 2
```

This processes the second batch of 15,000 trajectories.

### Combine trajectory batching with other options

For example:

```bash
python main.py --dataset eVED --trajectory-batch 3 --skip-net-generation
```

This processes the third trajectory batch while reusing an already generated SUMO network.

### Run SUMO validation

```bash
python main.py --eved-veh-types EV --validation
```

The validation workflow currently uses eVED as its reference dataset.

---

# Project structure

A simplified project structure is:

```text
SUMO-EV-Consumption/
│
├── data/
│   └── trajectory_parser/
│       ├── interface.py
│       ├── eved_parser.py
│       └── ...
│
├── datasets/
│   ├── eVED/
│   ├── DLR_UT/
│   └── ...
│
├── pipelines/
│   ├── eVED_pipeline.py
│   ├── DLR_pipeline.py
│   └── ...
│
├── SUMO/
│   ├── sumo_files/
│   │   ├── config/
│   │   ├── custom/
│   │   └── output/
│   │
│   └── sumo_files_validation/
│       ├── config/
│       ├── custom/
│       └── output/
│
├── virtual_data/
│   └── dataset_generation.py
│
├── virtual_datasets/
│   ├── 20260815_eVED_001.csv
│   ├── ...
│   └── ...
│
├── main.py
├── .env
└── ...
```

### `data/`

Contains the common trajectory representation and the dataset-specific trajectory parsers.

### `datasets/`

Contains the original trajectory datasets used as input.

Each supported dataset has its own directory.

### `pipelines/`

Contains the dataset-specific execution pipelines.

Each pipeline coordinates parsing, network generation, route generation, SUMO simulation and virtual dataset generation for its corresponding dataset.

### `SUMO/`

Contains SUMO configuration and generated SUMO-related files.

`sumo_files/` contains the configuration used for normal dataset simulations, while `sumo_files_validation/` contains the configuration and reference resources used for validation.

Generated networks, routes and other execution-specific files are not intended to be committed to the repository.

### `virtual_data/`

Contains the logic responsible for generating virtual datasets from SUMO simulation results.

Currently it contains:

```text
virtual_data/
└── dataset_generation.py
```

### `virtual_datasets/`

Contains the virtual trajectory datasets generated by the tool.

Generated datasets use a naming convention such as:

```text
20260815_eVED_001.csv
```

where the filename identifies the generation date, source dataset and generated dataset number.

---

# Quick reference

| Argument                  | Purpose                                         |
| ------------------------- | ----------------------------------------------- |
| `--validation`            | Run the SUMO validation workflow                |
| `--dataset`               | Select the trajectory dataset                   |
| `--skip-net-generation`   | Reuse an existing SUMO 3D network               |
| `--skip-route-generation` | Reuse existing SUMO routes                      |
| `--trajectory-batch`      | Select the 15,000-trajectory batch to process   |
| `--eved-veh-types`        | Select ICE/HEV/PHEV/EV vehicles when using eVED |
| `--depart-delay`          | Set the departure delay between generated trips |

The `--skip-net-generation` and `--skip-route-generation` options can be combined. `--skip-route-generation` should not be used alone because route generation depends on the network being available.

`--trajectory-batch` defaults to `1` and can be used to divide large trajectory datasets into multiple batches of 15,000 trajectories.

## Author

**Giuseppe Tarallo**  
University of Naples Federico II