import logging
import os

from datetime import datetime

from .utils.logging import initalise_logger, write_log_header, write_log_footer
from .utils.misc import (
    get_config_obj,
    execute_and_yield_output,
    execute_and_log,
    check_remote_dir_exists,
)

from .utils import create_cmd
from .utils.options import Options
from .utils.paths import Paths
from .utils.proc_rsync_out import parse_line
from .utils.emails import Email

from pathlib import Path


class ConfigFileError(Exception):
    pass


class SourceDirectoryError(Exception):
    pass


class DestinationDirectoryError(Exception):
    pass


class Synchronise:
    def __init__(
        self,
        config_file,
        log_filename,
        log_level="DEBUG",
        tar_flags=["-cvlpf"],
        untar_flags=["-xvpf"],
        rsync_flags=["-aP"],
        tar=True,
        untar=True,
        delete_source_tar=True,
        delete_destination_tar=True,
        create_dest=False,
        create_dest_parents=True,
        exclude_log_file=True,
        change_permissions=True,
        permissions="770",
        exclude_all_synchro_logs=False,
        write_transfer_done=True,
        send_transfer_notifications=False,
    ):
        self.start_time = datetime.now()
        self.sync_ready = False
        self.config_file = config_file
        self.log_level = log_level
        self.rsync_flags = rsync_flags
        self.tar_flags = tar_flags
        self.flags = untar_flags
        self.exclude_all_synchro_logs = exclude_all_synchro_logs
        self.write_transfer_done = write_transfer_done
        self.send_transfer_notifications = send_transfer_notifications

        self.config = []
        self.rsync_destination_directory = []
        self.create_dest_parents = create_dest_parents
        self.exclude_log_file = exclude_log_file
        self.dest_exists = []

        self.change_permissions = change_permissions

        self.mkdir_string = None
        self.tar_string = None
        self.untar_string = None
        self.delete_destination_tarball_string = None
        self.rsync_string = None
        self.rsync_dry_string = None
        self.change_ownership_string = []
        self.change_permission_string = []

        self.files_to_sync = []

        self.read_config()
        self.paths = Paths(self.config, log_filename)
        self.check_source_directory()
        self.options = Options(
            self.config,
            create_dest,
            tar,
            untar,
            permissions,
            delete_source_tar,
            delete_destination_tar,
        )
        self.check_sync_ready()

        if self.sync_ready:
            self.prep_sync()
            self.setup_logging()
            self.write_log_header()

        self.email_on_start_cmd = None
        self.email_on_end_cmd = None
        self.prep_email()

    def check_sync_ready(self):
        """
        Ensure the files are in place before starting sync
        """
        if self.paths.destination_directory is None:
            logging.error(
                "Destination directory is not set in the config file"
            )
            self.abort()
            self.sync_ready = False
        elif self.check_transfer_in_prog_file():
            print("Existing transfer still in progress...")
            self.sync_ready = False
        else:
            if not self.check_transfer_done_file():
                self.transfer_check_ready_file()
            else:
                print("Transfer done file exists")
                self.sync_ready = False

        if not self.sync_ready:
            print("Not running synchronisation")

    def check_transfer_done_file(self):
        """
        Check whether the transfer done file (transfer.done) exists,
        signifying transfer has already taken place.
        """
        return self.paths.transfer_done_file.exists()

    def check_transfer_in_prog_file(self):
        return self.paths.transfer_in_prog_file.exists()

    def transfer_check_ready_file(self):
        """
        Check whether the transfer ready file (e.g. ready.txt) exists,
        signifying transfer should begin.
        """
        if self.paths.transfer_ready_file is not None:
            if self.paths.transfer_ready_file.exists():
                self.sync_ready = True
            else:
                print(
                    f"Transfer ready file: {self.paths.transfer_ready_file} "
                    f"does not exist."
                )
        else:
            self.sync_ready = True

    def prep_email(self):
        self._prep_email_on_start()
        self._prep_email_on_end()

    def _prep_email_on_start(self):
        if self.options.email_on_start:
            subject = f"synchro-transfer-start-{self.start_time}"
            recipient = self.options.email_address
            self.email_on_start_cmd = Email(
                subject=subject, recipient=recipient
            ).cmd
        else:
            self.email_on_start_cmd = Email.null().cmd

    def _prep_email_on_end(self):
        if self.options.email_on_end:
            subject = f"synchro-complete-{self.start_time}"
            recipient = self.options.email_address
            attachment = self.paths.email_file
            self.email_on_end_cmd = Email(
                subject=subject,
                recipient=recipient,
                message_body_file=attachment,
            ).cmd
        else:
            self.email_on_end_cmd = Email.null().cmd

    def write_email_file(self):
        with open(self.paths.email_file, "w") as f:
            f.write("-- Transfer summary:\n\n")

            with open(self.paths.log_filename, "r") as g:
                line = g.readline()

                while not line.startswith(
                    "---Starting dry run:"
                ):  # TODO: fix start/end of email component
                    line = g.readline()

                while not line.startswith("---Dry run complete:"):
                    line = g.readline()

                    if not line.startswith("---Dry run complete:"):
                        f.write(line)

    def send_email_start(self):
        if self.email_on_start_cmd is not None:
            logging.debug(
                f"Sending start of transfer email to "
                f"{self.options.email_address}"
            )
            execute_and_log(self.email_on_start_cmd)

    def send_email_end(self):
        if self.email_on_end_cmd is not None:
            logging.debug(
                f"Sending end of transfer email to "
                f"{self.options.email_address}"
            )
            self.write_email_file()
            execute_and_log(self.email_on_end_cmd)
            os.remove(self.paths.email_file)

    def prep_sync(self):
        self.check_inputs()

        if self.options.tar:
            self.prep_tar_string()
            if self.options.untar:
                self.prep_untar_string()
                if self.options.delete_destination_tar:
                    self.prep_delete_destination_tarball_string()

        if self.options.tar:
            self.files_to_sync = self.paths.tar_archive
        else:
            self.files_to_sync = self.paths.source_directory

        self.prep_rsync_string()
        self.get_ownership()
        self.prep_change_ownership_permission_strings()

    def check_source_directory(self):
        """
        Check whether the source directory exists before proceeding
        """
        if not self.paths.source_directory.exists():
            error = (
                f"Source directory: {self.paths.source_directory} "
                f"does not exist."
            )
            raise SourceDirectoryError(error)

    def check_inputs(self):
        """
        Check inputs are correct for the synchronisation to proceed
        """
        self.check_destination_directory()

    def check_destination_directory(self):
        """
        Check if destination directory exists, and if it doesn't,
        either create it, or raise an error (depending on config).
        """
        if self.paths.remote_destination:
            if not self.remote_dest_exists():
                self.deal_with_missing_destination_directory()
        else:
            if not self.paths.destination_directory.exists():
                self.deal_with_missing_destination_directory()

    def remote_dest_exists(self):
        """
        Check if the destination directory exists on a remote machine.
        """
        return check_remote_dir_exists(
            self.paths.remote_host, self.paths.local_destination
        )

    def deal_with_missing_destination_directory(self):
        """
        If destination directory doesn't exist, either create it, or raise an
        error (depending on config).
        """
        if self.options.create_dest:
            self.create_dest_dir()
        else:
            self.raise_destination_dir_error()

    def create_dest_dir(self):
        """
        Create the destination directory, either locally or on a remote machine
        :return:
        """
        if self.paths.remote_destination:
            self.create_remote_directory()
        else:
            self.paths.destination_directory.mkdir(
                parents=self.create_dest_parents
            )

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
            f"Destination directory: {self.paths.destination_directory} "
            f"does not exist."
        )
        logging.error(error)
        self.abort()
        raise DestinationDirectoryError(error)

    def read_config(self):
        """
        Read the .conf file to set up the synchronisation
        """
        if not self.config_file.exists():
            raise ConfigFileError(
                f"No config file exists at: {self.config_file}"
            )
        self.config = get_config_obj(self.config_file)

    def setup_logging(self):
        """
        Begin logging (to stdout and to file)
        """
        initalise_logger(self.paths.log_filename, file_level=self.log_level)

    def write_log_header(self):
        """
        Write a standardised header to the log file
        """

        write_log_header(
            self.start_time,
            self.paths.source_directory,
            self.paths.destination_directory,
            self.rsync_string,
            self.tar_string,
            self.untar_string,
            delete_dest_tarball_string=self.delete_destination_tarball_string,
        )

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
            self.paths.remote_host,
            mkdir_command,
            self.paths.local_destination,
        ]

    def prep_tar_string(self):
        """
        Create tar command, including '-C' flag to move to directory before
        archiving.
        """

        if self.exclude_all_synchro_logs:
            self.tar_string = [
                "tar",
                f"--exclude={self.paths.log_filename.name}",
                "--exclude=synchro*.log",
                "--exclude=transfer.ongoing",
            ]
        elif self.exclude_log_file:
            self.tar_string = [
                "tar",
                f"--exclude={self.paths.log_filename.name}",
                "--exclude=transfer.ongoing",
            ]
        else:
            self.tar_string = [
                "tar",
                "--exclude=transfer.ongoing",
            ]

        cmd = [
            *self.tar_flags,
            str(self.paths.tar_archive),
            "-C",
            str(self.paths.source_directory),
            ".",
        ]
        self.tar_string = self.tar_string + cmd

    def prep_rsync_string(self):
        """
        Create command to run rsync
        """
        if not self.options.tar:
            files_to_sync = str(self.files_to_sync) + "/"
        else:
            files_to_sync = self.files_to_sync

        exclusion_string = [
            f"{self.paths.log_filename}",
            f"{self.paths.transfer_in_prog_file}",
        ]
        exclusion_string = [
            os.path.split(es)[1] for es in exclusion_string
        ] + ["synchro*.log"]
        exclusion_string = ["--exclude=" + es for es in exclusion_string]

        if self.exclude_all_synchro_logs:
            pass
        elif self.exclude_log_file:
            exclusion_string = exclusion_string[:-1]
        else:
            exclusion_string = exclusion_string[1]

        self.rsync_string = [
            "rsync",
            *self.rsync_flags,
            *exclusion_string,
            files_to_sync,
            str(self.paths.destination_directory),
        ]

        self.rsync_dry_string = [
            "rsync",
            "-ai",
            *exclusion_string,
            "--dry-run",
            str(self.paths.source_directory) + "/",
            str(self.paths.destination_directory),
        ]

    def prep_untar_string(self):
        """
        Create untar command, including '-C' flag to move to directory before
        archiving.
        """
        self.untar_string = [
            "tar",
            *self.flags,
            str(self.paths.dest_tar_archive),
            "-C",
            str(self.paths.local_destination),
        ]
        if self.paths.remote_destination:
            self.untar_string = create_cmd.add_ssh_prefix(
                self.untar_string, self.paths.remote_host
            )

    def prep_change_ownership_permission_strings(self):
        """
        Create command change permissions at destination
        """
        (
            self.change_ownership_string,
            self.change_permission_string,
        ) = create_cmd.change_ownership_permission(
            self.options.tar,
            self.options.untar,
            self.options.delete_destination_tar,
            self.options.owner,
            self.options.group,
            self.options.permissions,
            self.paths.dest_tar_archive,
            self.paths.local_destination,
            self.paths.remote_host,
            self.paths.remote_destination,
        )

    def prep_delete_destination_tarball_string(self):
        self.delete_destination_tarball_string = (
            create_cmd.delete_destination_tarball_string(
                self.paths.dest_tar_archive,
                self.paths.remote_host,
                self.paths.remote_destination,
            )
        )

    def _create_in_progress_file(self):
        """
        Creates temporary file to indicate synchro is in progress
        """
        Path.touch(self.paths.transfer_in_prog_file, exist_ok=False)

    def _delete_in_progress_file(self):
        os.remove(self.paths.transfer_in_prog_file)

    def start_sync(self):
        """
        Run the full synchronisation workflow
        """
        if self.sync_ready:
            self._start_sync()

    def _start_sync(self):
        logging.debug("Checking for progress file")
        self._create_in_progress_file()

        files_to_transfer = self._run_rsync_dry()

        if files_to_transfer:
            self.send_email_start()

            if self.options.tar:
                logging.debug("Starting tar archiving")
                self.run_tar()

            logging.debug("Starting rsync")
            self.run_rsync()
            logging.debug("Rsync completed")

            if self.options.untar:
                logging.debug("Untaring files")
                self.run_untar()

                if self.options.delete_destination_tar:
                    logging.debug("Removing destination tar archive")
                    self.run_destination_tar_deletion()
            else:
                logging.debug("Not untaring files")

            if self.write_transfer_done:
                logging.debug("Writing 'transfer.done' file")
                self.write_transfer_done_file()
            else:
                logging.debug("Warning: Not writing 'transfer.done' file")

            if self.options.delete_source_tar:
                logging.debug("Removing source tar archive ")
                self.run_delete_source_tar()

            logging.debug("Setting destination ownership and permissions")
            self.set_ownership_permissions()

            self.send_email_end()

        logging.debug("Removing 'transfer.ongoing' file")
        self._delete_in_progress_file()

        self.write_log_footer()

    def get_ownership(self):
        """
        Get ownership of source directory so they can be set the same at
        destination
        """
        if self.options.owner is None:
            self.options.owner = self.paths.source_directory.owner()
        if self.options.group is None:
            self.options.group = self.paths.source_directory.group()

    def run_tar(self):
        execute_and_log(self.tar_string)

    def run_destination_tar_deletion(self):
        execute_and_log(self.delete_destination_tarball_string)

    def _run_rsync_dry(self):
        logging.debug("\n---Starting dry run:")

        perform_transfer = False

        for output in execute_and_yield_output(self.rsync_dry_string):
            sync_required, message = parse_line(output)
            perform_transfer = perform_transfer or sync_required
            logging.debug(message.strip("\n"))
        logging.debug(
            "---Dry run complete: {}changes detected\n".format(
                "" if perform_transfer else "no "
            )
        )
        return perform_transfer

    def run_rsync(self):
        execute_and_log(self.rsync_string)

    def run_untar(self):
        execute_and_log(self.untar_string)

    def run_delete_source_tar(self):
        self.paths.tar_archive.unlink()

    def set_ownership_permissions(self):
        """
        Set ownership at destination
        """
        if self.change_permissions:
            execute_and_log(self.change_ownership_string)
            execute_and_log(self.change_permission_string)

    def write_transfer_done_file(self):
        self.paths.transfer_done_file.touch()

    def abort(self):
        """
        Stop an already running synchronisation
        """
        logging.error("SYNC FAILED")
        self.write_log_footer()
        self._delete_in_progress_file()
        # TODO: Build email notification

    def write_log_footer(self):
        write_log_footer(self.start_time)


def run_sychronisation(
    config_file,
    log_file,
    change_permissions=True,
    write_transfer_done=True,
    exclude_all_synchro_logs=False,
):
    synchro = Synchronise(
        config_file,
        log_file,
        change_permissions=change_permissions,
        write_transfer_done=write_transfer_done,
        exclude_all_synchro_logs=exclude_all_synchro_logs,
    )
    synchro.start_sync()
