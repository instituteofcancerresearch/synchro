from pathlib import Path
from synchro.utils import misc


def test_split_pathlib():
    path = Path("user@remote:/path/to/dir")
    components = misc.split_pathlib(path)
    assert components[0] == "user@remote"
    assert components[1] == "/path/to/dir"
