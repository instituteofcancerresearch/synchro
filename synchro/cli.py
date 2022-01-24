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
        dest="config_file",
        type=Path,
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
    parser.add_argument(
        "--no-permission-change",
        dest="change_permissions",
        action="store_false",
        help="Don't change permissions or ownership of destination files. "
        "Useful for debugging or if not running as root.",
    )

    return parser


def main():
    args = cli_parser().parse_args()
    run_sychronisation(
        args.config_file, args.log_file, args.change_permissions
    )


if __name__ == "__main__":
    main()
