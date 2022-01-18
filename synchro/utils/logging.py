import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


def initalise_logger(
    filename: str, print_level: str = "INFO", file_level: str = "DEBUG"
) -> logging.Logger:
    """
    Start logging to file and stdout
    :param filename: Where to save the logs to
    :param print_level: What level of logging to send to stdout.
    :param file_level: What level of logging to print to file.
    """

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, file_level))

    formatter = logging.Formatter()
    formatter.datefmt = "%Y-%m-%d %H:%M:%S %p"

    if filename is not None:
        fh = logging.FileHandler(filename)
        fh.setLevel(getattr(logging, file_level))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, print_level))
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def write_log_header(
    start_time: datetime,
    source_directory: Path,
    destination_directory: Path,
    rsync_string: str,
    tar_string: Optional[str] = None,
    untar_string: Optional[str] = None,
    delete_dest_tarball_string: Optional[str] = None,
):
    """
    Write a standardised header to the log file
    """

    logging.debug("************ TRANSFER LOG ************")
    logging.info(
        f"Transferring directory: {source_directory} to "
        f"{destination_directory}"
    )
    logging.debug(
        f"Transfer started: " f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}"
    )
    logging.debug(f"Source directory: {source_directory}")
    logging.debug(f"Destination directory: {destination_directory}")
    if tar_string is not None:
        logging.debug(f"tar command: {tar_string}")
    logging.debug(f"rsync command: {rsync_string}")
    if untar_string is not None:
        logging.debug(f"untar command: {untar_string}")
    if delete_dest_tarball_string is not None:
        logging.debug(f"deletion command: {delete_dest_tarball_string}")

    logging.debug("**************************************\n")
    logging.debug("Starting log")


def write_log_footer(start_time: datetime):
    """
    Write a standardised footer to the log file
    """
    end_time = datetime.now()
    transfer_duration = end_time - start_time
    logging.info("Transfer ended")
    logging.debug(
        f"Transfer ended at:  " f"{start_time.strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    logging.debug(f"Time taken: {transfer_duration}")
