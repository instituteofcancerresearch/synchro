import logging
import subprocess
from configparser import ConfigParser
from pathlib import Path
from typing import Union


def get_config_obj(config_path: Union[Path, str]) -> ConfigParser:
    """
    Read conf file
    From https://stackoverflow.com/questions/2885190

    :param config_path: Path to config file
    :return: ConfigParser object
    """

    config_path = str(config_path)
    parser = ConfigParser()
    with open(config_path) as stream:
        parser.read_string("[config]\n" + stream.read())
    return parser


def execute_and_yield_output(cmd):
    """
    Run terminal command and yield output
    From https://stackoverflow.com/questions/4417546/

    :param cmd: Terminal command to run
    """
    popen = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def execute_and_log(cmd, rstrip=True, skip_empty=True):
    """
    Execute a terminal command, and log the output using the standard
    logging library

    :param cmd: Command to run
    :param rstrip: Strip the output of trailing new line
    :param skip_empty: Don't log empty lines
    """
    for string in execute_and_yield_output(cmd):
        if rstrip:
            string = string.rstrip("\n")
        if skip_empty:
            if string != "":
                logging.debug(string)
        else:
            logging.debug(string)


def split_pathlib(path, separator=":"):
    """
    Split a pathlib object
    :param path: Pathlib object
    :param separator: Character used to split
    :return: Parts of the path (before & after split character)
    """
    path = str(path)
    components = path.split(separator)
    return components


def check_pathlib_remote(path: Path) -> bool:
    """
    Check whether a pathlib object refers to a remote directory
    (assumes a colon separates the address and directory)
    :param path: Pathlib object
    :return: True if pathlib object refers to remote directory
    """
    components = split_pathlib(path)
    if len(components) > 1:
        return True
    else:
        return False


def return_pathlib_remote_components(path: Path) -> list[str]:
    """
    Alias for splitting pathlib using default split (colon) character
    Returns the  address and directory

    :param path: Pathlib object
    :return: Machine address and local directory
    """
    return split_pathlib(path)


def check_remote_dir_exists(host, directory, return_string="dir_exists"):
    """
    Check if a directory on a remote machine exists via ssh
    :TODO improve untidy implementation

    :param host: user@remote, needs ssh keys set up
    :param directory: Path to local directory
    :param return_string: Some string to return if directory exists
    :return: bool
    """
    directory = str(directory)
    cmd = ["ssh", host, f"[ -d '{directory}' ] && echo '{return_string}'"]
    try:
        for string in execute_and_yield_output(cmd):
            if string == f"{return_string}\n":
                return True
        return False
    except subprocess.CalledProcessError:
        return False
