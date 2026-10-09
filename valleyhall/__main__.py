import argparse
import json
from .channels import channel_status, reference_regime
from .replay import load_checked, replay


def main():
    parser = argparse.ArgumentParser(description="Kinematic screening and archived-estimate replay")
    commands = parser.add_subparsers(dest="command", required=True)
    screen = commands.add_parser("screen")
    screen.add_argument("--frequency", type=float, required=True, help="f=a/lambda_0")
    screen.add_argument("--kx", type=float, default=1/3, help="in 2*pi/a units, within [-0.5,0.5]")
    screen.add_argument("--upper-index", type=float, required=True)
    screen.add_argument("--lower-index", type=float, required=True)
    archived = commands.add_parser("replay")
    archived.add_argument("directory", help="path to examples/design_b")
    args = parser.parse_args()
    try:
        if args.command == "screen":
            result = {"upper": channel_status(args.frequency, args.kx, args.upper_index),
                      "lower": channel_status(args.frequency, args.kx, args.lower_index),
                      "reference_classification": reference_regime(args.frequency, max(args.upper_index, args.lower_index)),
                      "scope": "Channel availability only; no radiation rate or mode existence inferred. Classification is at the input frequency only."}
        else:
            result = {"scope": "Archived supercell vertical-radiation estimate; physical Q unvalidated.",
                      "walls": replay(load_checked(args.directory))}
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
