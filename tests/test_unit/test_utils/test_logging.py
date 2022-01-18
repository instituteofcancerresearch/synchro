import logging
from datetime import datetime
from synchro.utils.logging import (
    initalise_logger,
    write_log_header,
    write_log_footer,
)
from ...utils.utils import setup_simple_log


def test_initalise_logger(tmpdir):
    log_file = tmpdir / "log.log"
    initalise_logger(log_file)
    logging.info("TEST LOGGING")
    with open(log_file) as f:
        lines = f.readlines()
    assert lines[0] == "TEST LOGGING\n"


def test_write_log_header(tmpdir):
    log_file = tmpdir / "log.log"
    setup_simple_log(log_file)
    start_time = datetime.now()
    write_log_header(
        start_time,
        tmpdir,
        tmpdir / "dest",
        "rsync string",
        tar_string="tar string",
        untar_string="untar string",
        delete_dest_tarball_string="delete string",
    )

    with open(log_file) as f:
        lines = f.readlines()
    assert lines[0] == "************ TRANSFER LOG ************\n"
    assert (
        lines[1] == f"Transferring directory: "
        f"{str(tmpdir)} to {str(tmpdir / 'dest')}\n"
    )
    assert lines[6] == "rsync command: rsync string\n"
    assert lines[8] == "deletion command: delete string\n"


def test_write_log_footer(tmpdir):
    log_file = tmpdir / "log.log"
    setup_simple_log(log_file)
    start_time = datetime.now()
    write_log_footer(start_time)

    with open(log_file) as f:
        lines = f.readlines()
    assert lines[0] == "Transfer ended\n"
