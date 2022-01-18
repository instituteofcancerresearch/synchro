from pathlib import Path
from synchro.utils import misc
from ...utils.utils import create_conf_file, setup_simple_log


def test_get_config_obj(tmpdir):
    destination = tmpdir / "dest"
    create_conf_file(tmpdir, destination)
    config = misc.get_config_obj(tmpdir / "synchro.conf")
    assert config.get("config", "destination") == destination
    assert config.get("config", "untar") == "y"


def test_execute_and_yield_output(tmpdir):
    dest_dir = tmpdir / "test"
    cmd = ["mkdir", str(dest_dir)]
    misc.execute_and_yield_output(cmd)
    for _ in misc.execute_and_yield_output(cmd):
        pass
    assert dest_dir.exists()


def test_execute_and_log(tmpdir):
    log_file = tmpdir / "log.log"
    setup_simple_log(log_file)

    cmd = ["echo", "test"]
    misc.execute_and_log(cmd)
    with open(log_file) as f:
        lines = f.readlines()
    assert lines[0] == "test\n"


def test_split_pathlib():
    path = Path("user@remote:/path/to/dir")
    components = misc.split_pathlib(path)
    assert components[0] == "user@remote"
    assert components[1] == "/path/to/dir"


def test_check_pathlib_remote():
    assert misc.check_pathlib_remote(Path("user@remote:/path/to/dir"))
    assert not misc.check_pathlib_remote(Path("/path/to/dir"))


def test_return_pathlib_remote_components():
    path = Path("user@remote:/path/to/dir")
    components = misc.return_pathlib_remote_components(path)
    assert components[0] == "user@remote"
    assert components[1] == "/path/to/dir"
