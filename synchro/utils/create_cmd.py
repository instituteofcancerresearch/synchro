class DestinationDirectoryError(Exception):
    pass


def add_ssh_prefix(cmd: list[str], remote_host: str) -> list:
    """
    Prefix a command with "ssh <remote_address>" for remote use
    :param cmd: Command to be run remotely
    :param remote_host: Remote machine address
    :return: Command with prefix
    """
    ssh_string = ["ssh", remote_host]
    return ssh_string + cmd


def change_ownership_permission(
    tar,
    untar,
    delete_destination_tar,
    owner,
    group,
    permissions,
    dest_tar_archive,
    local_destination,
    remote_host,
    remote_destination=False,
):
    """
    Create command change permissions at destination

    Command depends on whether the tar archive, the destination directory
    or both will remain at the destination.
    """
    if tar:
        if delete_destination_tar and not untar:
            raise DestinationDirectoryError(
                "Tar archive deleted, but not extracted. Aborting"
            )

    new_ownership = owner + ":" + group
    chown_string = ["chown", "-R", new_ownership]
    chmod_string = ["chmod", "-R", permissions]

    if tar and untar and not delete_destination_tar:
        change_archive = True
        change_dest = True
    elif tar and untar and delete_destination_tar:
        change_archive = False
        change_dest = True
    elif tar and not untar:
        change_archive = True
        change_dest = False
    elif not tar:
        change_archive = False
        change_dest = True

    if change_archive and change_dest:
        change_ownership_string = (
            chown_string + [str(dest_tar_archive)] + [str(local_destination)]
        )

        change_permission_string = (
            chmod_string + [str(dest_tar_archive)] + [str(local_destination)]
        )
    elif change_dest:
        change_ownership_string = chown_string + [str(local_destination)]
        change_permission_string = chmod_string + [str(local_destination)]
    elif change_archive:
        change_ownership_string = chown_string + [str(dest_tar_archive)]
        change_permission_string = chmod_string + [str(dest_tar_archive)]

    if remote_destination:
        change_ownership_string = add_ssh_prefix(
            change_ownership_string, remote_host
        )
        change_permission_string = add_ssh_prefix(
            change_permission_string, remote_host
        )

    return change_ownership_string, change_permission_string


def delete_destination_tarball_string(
    dest_tar_archive, remote_host, remote_destination=False
):
    """
    Create command to delete tar archive after untar
    """
    delete_dest_tarball_string = [
        "rm",
        "-v",
        str(dest_tar_archive),
    ]
    if remote_destination:
        delete_dest_tarball_string = add_ssh_prefix(
            delete_dest_tarball_string,
            remote_host,
        )
    return delete_dest_tarball_string
