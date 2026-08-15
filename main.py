import time

from dotenv import load_dotenv

from arguments import args

from SUMO.sumo_validation import runSUMOvalidation

from pipelines.eVED_pipeline import runEVEDPipeline
from pipelines.DLR_pipeline import runDLRPipeline

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
    case "DLR":
        runDLRPipeline()
    case _:
        print("Invalid dataset!")
        quit()


# Print
print(
    f"\rVirtual dataset generated in {time.perf_counter() - start:.2f}s"
)
