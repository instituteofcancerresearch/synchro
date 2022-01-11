from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
)

from pathlib import Path
from synchro.sync import run_sychronisation


def cli_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument_group("Synchro options")

    parser.add_argument(
        dest="source_directory",
        type=Path,
        help="Directory to be synchronised",
    )

    parser.add_argument(
        "--config-file",
        dest="config_file",
        type=str,
        default="synchro.conf",
        help="Name of the config file",
    )
    parser.add_argument(
        "-l",
        "--log-file",
        dest="log_file",
        default=None,
        help="File to log to. Otherwise defaults to "
        "'destination_directory/synchro.log",
    )

    return parser


def main():
    args = cli_parser().parse_args()
    source_directory = args.source_directory
    config_file = source_directory / args.config_file
    run_sychronisation(source_directory, config_file, args.log_file)


if __name__ == "__main__":
    main()
