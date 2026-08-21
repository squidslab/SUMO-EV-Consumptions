import time

from dotenv import load_dotenv

from arguments import args

from SUMO.sumo_validation import runSUMOvalidation

from pipelines.eVED_pipeline import runEVEDPipeline
from pipelines.DLR_pipeline import runDLRPipeline
from pipelines.pNEUMA_pipeline import runPNEUMAPipeline

# Load env configuration
load_dotenv()

# Initialize timer
start = time.perf_counter()

# If validation execution has been set, run it then quit.
if args.validation:
    runSUMOvalidation()
    quit()

# Select pipeline to exectue based on given settings
match args.dataset:
    case "eVED":
        runEVEDPipeline()
    case "pNEUMA":
        runPNEUMAPipeline()
    case "DLR":
        runDLRPipeline()
    case _:
        print("Invalid dataset!")
        quit()

# Log virtual dataset generation info
print(
    f"\r\nVirtual dataset generated in {time.perf_counter() - start:.2f}s"
)
