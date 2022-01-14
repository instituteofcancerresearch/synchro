def add_ssh_prefix(cmd, remote_host):
    """
    Prefix a command with "ssh <remote_address>" for remote use
    :param cmd: Command to be run remotely
    :return: Command with prefix
    """
    ssh_string = ["ssh", remote_host]
    return ssh_string + cmd
