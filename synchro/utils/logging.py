import sys
import logging

from datetime import datetime


def initalise_logger(filename, print_level="INFO", file_level="DEBUG"):
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
    start_time,
    source_directory,
    destination_directory,
    tar_string,
    rsync_string,
    untar_string,
    delete_destination_tar=False,
    delete_dest_tarball_string=None,
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
    logging.debug(f"tar command: {tar_string}")
    logging.debug(f"rsync command: {rsync_string}")
    if untar_string:
        logging.debug(f"untar command: {untar_string}")
    if delete_destination_tar:
        logging.debug(f"deletion command: {delete_dest_tarball_string}")

    logging.debug("**************************************\n")
    logging.debug("Starting log")


def write_log_footer(start_time):
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
