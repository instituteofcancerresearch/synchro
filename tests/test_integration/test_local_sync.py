import sys
from pathlib import Path
from synchro.cli import main as synchro_run


def create_test_files(directory):
    (directory / "test1.txt").touch()
    (directory / "test2.txt").touch()
    (directory / "test_dir").mkdir()


def create_conf_file(source_dir, dest_dir):
    conf_file = source_dir / "synchro.conf"
    with open(conf_file, "w") as f:
        f.write(f"destination = {dest_dir}\n")
        f.write("untar = y\n")
        f.write("create_dest = y\n")


def test_local_sync(tmpdir):
    tmpdir = Path(tmpdir)
    source_dir = tmpdir / "source"
    source_dir.mkdir(exist_ok=True)

    create_test_files(source_dir)
    dest_dir = tmpdir / "dest"
    create_conf_file(source_dir, dest_dir)

    sys.argv = ["synchro", str(source_dir)]
    synchro_run()

    assert len(list(dest_dir.iterdir())) == 4
