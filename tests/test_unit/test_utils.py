from pathlib import Path
from synchro import utils


def test_split_pathlib():
    path = Path("user@remote:/path/to/dir")
    components = utils.split_pathlib(path)
    assert components[0] == "user@remote"
    assert components[1] == "/path/to/dir"
