from synchro.utils import create_cmd


def test_add_ssh_prefix():
    cmd = ["mkdir test"]
    remote_host = "8.8.8.8"
    assert create_cmd.add_ssh_prefix(cmd, remote_host) == [
        "ssh",
        remote_host,
        cmd[0],
    ]
