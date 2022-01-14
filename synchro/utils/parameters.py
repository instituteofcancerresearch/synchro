import configparser
import logging


class Options:
    def __init__(
        self,
        config,
        create_dest,
        tar,
        untar,
        permissions,
        owner=None,
        group=None,
    ):

        self.create_dest = try_set_boolean_with_default(
            config, create_dest, "create_dest"
        )

        self.tar, self.untar = set_tar_options(
            config, run_tar=tar, run_untar=untar
        )
        self.owner, self.group = set_ownership(config, owner, group)
        self.permissions = set_permissions(config, permissions)


def set_ownership(config, owner, group):
    owner = try_set_parameter(config, owner, "owner")
    group = try_set_parameter(config, group, "group")
    return owner, group


def set_permissions(config, permissions):
    return try_set_parameter(config, permissions, "permissions")


def set_tar_options(config, run_tar=True, run_untar=False):
    run_tar = try_set_boolean_with_default(config, run_tar, "tar")
    if run_tar:
        run_untar = try_set_boolean_with_default(config, run_untar, "untar")
    else:
        run_untar = False
    return run_tar, run_untar


def try_set_parameter(
    config, parameter, parameter_config_entry, config_string="config"
):
    try:
        parameter = config.get(config_string, parameter_config_entry)
    except configparser.NoOptionError:
        pass
    return parameter


def try_set_boolean_with_default(
    config, parameter, parameter_config_entry, config_string="config"
):
    try:
        parameter = (
            True
            if config.get(config_string, parameter_config_entry) == "y"
            else False
        )
    except configparser.NoOptionError:
        logging.warning(
            f"{parameter_config_entry} option not set in config file. "
            f"Setting to: {parameter}"
        )
    return parameter
