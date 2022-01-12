import configparser
import logging

from datetime import datetime
from pathlib import Path

from .utils import (
    initalise_logger,
    get_config_obj,
    execute_and_log,
    check_pathlib_remote,
    return_pathlib_remote_components,
    check_remote_dir_exists,
)


class ConfigFileError(Exception):
    pass


class SourceDirectoryError(Exception):
    pass


class DestinationDirectoryError(Exception):
    pass


class Synchronise:
    def __init__(
        self,
        source_directory,
        config_file,
        log_file,
        log_level="DEBUG",
        tar_options=["-cvlpf"],
        untar_options=["-xvf"],
        rsync_options=["-aP"],
        untar=False,
        delete_tarball=True,
        create_dest=False,
        create_dest_parents=True,
        exclude_log_file=True,
    ):
        self.sync_ready = False
        self.source_directory = source_directory
        self.config_file = config_file
        self.log_filename = log_file
        self.log_level = log_level
        self.rsync_options = rsync_options
        self.tar_options = tar_options
        self.untar_options = untar_options

        self.start_time = datetime.now()

        self.config = []
        self.destination_directory = []
        self.rsync_destination_directory = []
        self.transfer_ready_file = []
        self.untar = untar
        self.delete_tarball = delete_tarball
        self.create_dest = create_dest
        self.create_dest_parents = create_dest_parents
        self.exclude_log_file = exclude_log_file
        self.dest_exists = []
        self.tar_archive = []
        self.dest_tar_archive = []

        self.remote_dest = False
        self.remote_host = None
        self.local_destination = []

        self.mkdir_string = []
        self.tar_string = []
        self.untar_string = []
        self.delete_tarball_string = []
        self.rsync_string = []

        self.read_config()
        self.check_sync_ready()

        if self.sync_ready:
            self.prep_sync()
            self.setup_logging()
            self.write_log_header()

    def check_sync_ready(self):
        """
        Ensure the files are in place before starting sync
        """
        if not self.check_transfer_done_file():
            self.transfer_check_ready_file()
        else:
            self.sync_ready = False

        if not self.sync_ready:
            print("Not running synchronisation")

    def check_transfer_done_file(self):
        """
        Check whether the transfer done file (transfer.done) exists,
        signifying transfer has already taken place.
        """
        return self.transfer_done_file().exists()

    def transfer_check_ready_file(self):
        """
        Check whether the transfer ready file (e.g. ready.txt) exists,
        signifying transfer should begin.
        """
        if self.transfer_ready_file is not None:
            if self.transfer_ready_file.exists():
                self.sync_ready = True
            else:
                print(
                    f"Transfer ready file: {self.transfer_ready_file} "
                    f"does not exist."
                )
        else:
            self.sync_ready = True

    def prep_sync(self):
        self.get_log_filename()
        self.check_source_directory()
        self.check_remote_dest()
        self.check_inputs()
        self.prep_tar_archive_name()
        self.prep_tar_string()
        if self.untar:
            self.prep_untar_string()
            if self.delete_tarball:
                self.prep_delete_tarball_string()
        self.prep_rsync_string()

    def check_source_directory(self):
        """
        Check whether the source directory exists before proceeding
        """
        if not self.source_directory.exists():
            error = (
                f"Source directory: {self.source_directory} "
                f"does not exist."
            )
            raise SourceDirectoryError(error)

    def check_inputs(self):
        """
        Check inputs are correct for the sychronisation to proceed
        """
        self.check_destination_directory()

    def check_destination_directory(self):
        """
        Check if destination directory exists, and if it doesn't,
        either create it, or raise an error (depending on config).
        """
        if self.remote_dest:
            if not self.remote_dest_exists():
                self.deal_with_missing_destination_directory()
        else:
            if not self.destination_directory.exists():
                self.deal_with_missing_destination_directory()

    def remote_dest_exists(self):
        """
        Check if the destination directory exists on a remote machine
        :return: True if directory exists
        """
        return check_remote_dir_exists(
            self.remote_host, self.local_destination
        )

    def deal_with_missing_destination_directory(self):
        """
        If destination directory doesn't exist, either create it, or raise an
        error (depending on config).
        """
        if self.create_dest:
            self.create_dest_dir()
        else:
            self.raise_destination_dir_error()

    def create_dest_dir(self):
        """
        Create the destination directory, either locally or on a remote machine
        :return:
        """
        if self.remote_dest:
            self.create_remote_directory()
        else:
            self.destination_directory.mkdir(parents=self.create_dest_parents)

    def create_remote_directory(self):
        """
        Create the destination directory on a remote machine
        """
        self.prepare_mkdir_string()
        execute_and_log(self.mkdir_string)

    def raise_destination_dir_error(self):
        """
        Raise error if destination does not exist (and creation not selected)
        """
        error = (
            f"Destination directory: {self.destination_directory} "
            f"does not exist."
        )
        logging.error(error)
        self.abort()
        raise DestinationDirectoryError(error)

    def read_config(self):
        """
        Read the .conf file and parse to set up the synchronisation
        """
        if not self.config_file.exists():
            raise ConfigFileError(
                f"No config file exists at: {self.config_file}"
            )
        self.config = get_config_obj(self.config_file)
        self.parse_config()

    def parse_config(self):
        """
        Parse the .conf file to set up the synchronisation
        """
        try:
            self.destination_directory = Path(
                self.config.get("config", "destination")
            )
        except configparser.NoOptionError:
            logging.error(
                "Destination directory is not set in the " "config file"
            )
            self.abort()

        try:
            transfer_ready_file = self.config.get(
                "config", "transfer_ready_file"
            )
            self.transfer_ready_file = (
                self.source_directory / transfer_ready_file
            )
        except configparser.NoOptionError:
            self.transfer_ready_file = None

        try:
            self.untar = (
                True if self.config.get("config", "untar") == "y" else False
            )
        except configparser.NoOptionError:
            logging.warning(
                f"Untar option not set in config file. "
                f"Setting to: {self.untar}"
            )

        try:
            self.create_dest = (
                True
                if self.config.get("config", "create_dest") == "y"
                else False
            )
        except configparser.NoOptionError:
            logging.warning(
                f"Create destination option not set in config file. "
                f"Setting to: {self.create_dest}"
            )

    def check_remote_dest(self):
        """
        Check whether the destination directory is on a remote machine.
        If so, set the "remote_host" and "local_destination" properties
        appropriately
        """
        self.remote_dest = check_pathlib_remote(self.destination_directory)
        if self.remote_dest:
            remote_components = return_pathlib_remote_components(
                self.destination_directory
            )
            self.remote_host = remote_components[0]
            self.local_destination = Path(remote_components[1])
        else:
            self.local_destination = self.destination_directory

    def get_log_filename(self):
        """
        If no log filename is provided, create one based on the date/time
        """
        if self.log_filename is None:
            self.log_filename = self.source_directory / (
                datetime.now().strftime("synchro" + "_%Y-%m-%d_%H-%M-%S")
                + ".log"
            )

    def setup_logging(self):
        """
        Begin logging (to stdout and to file)
        """
        initalise_logger(self.log_filename, file_level=self.log_level)

    def write_log_header(self):
        """
        Write a standardised header to the log file
        """

        logging.debug("************ TRANSFER LOG ************")
        logging.info(
            f"Transferring directory: {self.source_directory} to "
            f"{self.destination_directory}"
        )
        logging.debug(
            f"Transfer started: "
            f"{self.start_time.strftime('%Y-%m-%d_%H-%M-%S')}"
        )
        logging.debug(f"Source directory: {self.source_directory}")
        logging.debug(f"Destination directory: {self.destination_directory}")
        logging.debug(f"tar command: {self.tar_string}")
        logging.debug(f"rsync command: {self.rsync_string}")
        if self.untar_string:
            logging.debug(f"untar command: {self.untar_string}")
        if self.delete_tarball:
            logging.debug(f"deletion command: {self.delete_tarball_string}")

        logging.debug("**************************************\n")
        logging.debug("Starting log")

    def prep_tar_archive_name(self):
        """
        Filename for the tar archive of the source directory
        """
        self.tar_archive = self.source_directory.parent / (
            self.source_directory.name + ".tar"
        )

    def prep_dest_tar_archive_path(self):
        """
        Filename for the tar archive of the destination directory
        """
        self.dest_tar_archive = self.local_destination / self.tar_archive.name

    def prepare_mkdir_string(self):
        """
        Create the command string needed to create the destination directory
        """
        if self.create_dest_parents:
            mkdir_command = "mkdir -p"
        else:
            mkdir_command = "mkdir"
        self.mkdir_string = [
            "ssh",
            self.remote_host,
            mkdir_command,
            self.local_destination,
        ]

    def prep_tar_string(self):
        """
        Create tar command, including '-C' flag to move to directory before
        archiving.
        """
        self.prep_dest_tar_archive_path()

        if self.exclude_log_file:
            self.tar_string = ["tar", f"--exclude={self.log_filename.name}"]
        else:
            self.tar_string = ["tar"]

        cmd = [
            *self.tar_options,
            str(self.tar_archive),
            "-C",
            str(self.source_directory),
            ".",
        ]
        self.tar_string = self.tar_string + cmd

    def prep_rsync_string(self):
        """
        Create command to run rsync
        """
        self.rsync_string = [
            "rsync",
            *self.rsync_options,
            str(self.tar_archive),
            str(self.destination_directory),
        ]

    def prep_untar_string(self):
        """
        Create untar command, including '-C' flag to move to directory before
        archiving.
        """
        self.untar_string = [
            "tar",
            *self.untar_options,
            str(self.dest_tar_archive),
            "-C",
            str(self.local_destination),
        ]
        if self.remote_dest:
            self.untar_string = self.add_ssh_prefix(self.untar_string)

    def prep_delete_tarball_string(self):
        """
        Create command to delete tar archive after untar
        """
        self.delete_tarball_string = [
            "rm",
            "-v",
            str(self.dest_tar_archive),
        ]
        if self.remote_dest:
            self.delete_tarball_string = self.add_ssh_prefix(
                self.delete_tarball_string
            )

    def add_ssh_prefix(self, cmd):
        """
        Prefix a command with "ssh <remote_address>" for remote use
        :param cmd: Command to be run remotely
        :return: Command with prefix
        """
        ssh_string = ["ssh", self.remote_host]
        return ssh_string + cmd

    def start_sync(self):
        """
        Run the full synchronisation workflow
        """
        if self.sync_ready:
            self._start_sync()

    def _start_sync(self):
        logging.debug("Starting tar archiving")
        self.run_tar()
        logging.debug("Starting rsync")
        self.run_rsync()
        logging.debug("Rsync completed")
        if self.untar:
            logging.debug("Untaring files")
            self.run_untar()
            if self.delete_tarball:
                logging.debug("Deleting tar archive")
                self.run_tar_deletion()
        else:
            logging.debug("Not untaring files")
        logging.debug("Writing 'transfer.done' file")
        self.write_transfer_done_file()
        self.write_log_footer()

    def run_tar(self):
        execute_and_log(self.tar_string)

    def run_tar_deletion(self):
        execute_and_log(self.delete_tarball_string)

    def run_rsync(self):
        execute_and_log(self.rsync_string)

    def run_untar(self):
        execute_and_log(self.untar_string)

    def write_transfer_done_file(self):
        self.transfer_done_file().touch()

    def transfer_done_file(self):
        return self.source_directory / "transfer.done"

    def abort(self):
        """
        Stop an already running synchronisation
        """
        logging.error("SYNC FAILED")
        self.write_log_footer()

    def write_log_footer(self):
        """
        Write a standardised footer to the log file
        """
        end_time = datetime.now()
        transfer_duration = end_time - self.start_time
        logging.info("Transfer ended")
        logging.debug(
            f"Transfer ended at:  "
            f"{self.start_time.strftime('%Y-%m-%d_%H-%M-%S')}"
        )

        logging.debug(f"Time taken: {transfer_duration}")


def run_sychronisation(source_directory, config_file, log_file):
    synchro = Synchronise(source_directory, config_file, log_file)
    synchro.start_sync()
