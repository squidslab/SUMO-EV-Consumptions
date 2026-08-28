from arguments import args
from paths import VALIDATION_CONFIG, VALIDATION_CUSTOM, VALIDATION_OUTPUT, CONFIG, CUSTOM, OUTPUT

configPath = VALIDATION_CONFIG if args.validation else CONFIG
customPath = VALIDATION_CUSTOM if args.validation else CUSTOM
outputPath = VALIDATION_OUTPUT if args.validation else OUTPUT
