import configparser
from pathlib import Path
from datetime import datetime

from synchro.utils.misc import (
    check_pathlib_remote,
    return_pathlib_remote_components,
)


class Paths:
    def __init__(self, config, log_filename):
        self.source_directory = self.set_source_directory(config)
        self.destination_directory = self.set_destination_directory(config)
        (
            self.local_destination,
            self.remote_host,
            self.remote_destination,
        ) = self.check_remote_dest(self.destination_directory)
        self.transfer_ready_file = self.set_transfer_initiation(
            config, self.source_directory
        )
        self.log_filename = self.set_log_filename(
            log_filename, self.source_directory
        )
        self.tar_archive = self.source_directory.parent / (
            self.source_directory.name + ".tar"
        )
        self.dest_tar_archive = self.local_destination / self.tar_archive.name
        self.transfer_done_file = self.source_directory / "transfer.done"

    @staticmethod
    def set_source_directory(config):
        try:
            source_directory = Path(config.get("config", "source"))
        except configparser.NoOptionError:
            source_directory = None
        return source_directory

    @staticmethod
    def set_destination_directory(config):
        try:
            destination_directory = Path(config.get("config", "destination"))
        except configparser.NoOptionError:
            destination_directory = None
        return destination_directory

    @staticmethod
    def check_remote_dest(destination_directory):
        """
        Check whether the destination directory is on a remote machine.
        If so, set the "remote_host" and "local_destination" properties
        appropriately
        """
        remote_destination = check_pathlib_remote(destination_directory)
        if remote_destination:
            remote_components = return_pathlib_remote_components(
                destination_directory
            )
            remote_host = remote_components[0]
            local_destination = Path(remote_components[1])
        else:
            local_destination = destination_directory
            remote_host = None

        return local_destination, remote_host, remote_destination

    @staticmethod
    def set_log_filename(log_filename, source_directory):
        """
        If no log filename is provided, create one based on the date/time
        """
        if log_filename is None:
            log_filename = source_directory / (
                datetime.now().strftime("synchro" + "_%Y-%m-%d_%H-%M-%S")
                + ".log"
            )
        return log_filename

    @staticmethod
    def set_transfer_initiation(config, source_directory):
        try:
            transfer_ready_file = config.get("config", "transfer_ready_file")
            transfer_ready_file = source_directory / transfer_ready_file
        except configparser.NoOptionError:
            transfer_ready_file = None

        return transfer_ready_file
