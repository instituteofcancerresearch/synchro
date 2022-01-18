import sys
import pytest
from pathlib import Path
from synchro.cli import main as synchro_run
from synchro.sync import SourceDirectoryError
from ..utils.utils import create_conf_file


def test_local_sync_4_files(tmpdir):
    # Run without creating or requiring a ready file
    _, dest_dir = prep_run_sync(
        tmpdir, create_ready_file=None, check_ready_file=None
    )
    assert len(list(dest_dir.iterdir())) == 4


def test_local_sync_no_untar(tmpdir):
    # Run without untar
    _, dest_dir = prep_run_sync(
        tmpdir, create_ready_file=None, check_ready_file=None, untar="n"
    )
    assert len(list(dest_dir.iterdir())) == 1


def test_local_sync_no_tar(tmpdir):
    # Run without tar
    _, dest_dir = prep_run_sync(
        tmpdir, create_ready_file=None, check_ready_file=None, tar="y"
    )
    assert len(list(dest_dir.iterdir())) == 4


def test_local_sync_5_files(tmpdir, ready_file="ready.txt"):
    # Create a ready file, but do not require it
    _, dest_dir = prep_run_sync(
        tmpdir, create_ready_file=ready_file, check_ready_file=None
    )
    assert len(list(dest_dir.iterdir())) == 5


def test_conditional_local_sync(tmpdir, ready_file="ready.txt"):
    # Create a ready file, and require it
    _, dest_dir = prep_run_sync(
        tmpdir, create_ready_file=ready_file, check_ready_file=ready_file
    )
    assert len(list(dest_dir.iterdir())) == 5


def test_conditional_local_sync_no_ready_file(tmpdir, ready_file="ready.txt"):
    # Don't create a ready file, and require it
    _, dest_dir = prep_run_sync(
        tmpdir, create_ready_file=None, check_ready_file=ready_file
    )
    assert dest_dir.exists() is False


def test_skip_with_done_file(tmpdir):
    # Test that transfer is skipped if already performed

    source_dir, dest_dir = prep_run_sync(
        tmpdir, create_ready_file=None, check_ready_file=None
    )
    assert dest_dir.exists()

    remove_path(dest_dir)
    sys.argv = ["synchro", str(source_dir)]
    synchro_run()
    assert dest_dir.exists() is False


def test_local_no_source(tmpdir):
    # Run without source dir
    with pytest.raises(SourceDirectoryError):
        run_sync(tmpdir / "course")


def remove_path(path: Path):
    """
    From https://stackoverflow.com/a/65230962/
    """
    if path.is_file() or path.is_symlink():
        path.unlink()
        return
    for p in path.iterdir():
        remove_path(p)
    path.rmdir()


def prep_directories(top_level_dir):
    source_dir = top_level_dir / "source"
    dest_dir = top_level_dir / "dest"
    source_dir.mkdir(exist_ok=True)

    return source_dir, dest_dir


def create_test_files(directory, ready_file=None):
    (directory / "test1.txt").touch()
    (directory / "test2.txt").touch()
    (directory / "test_dir").mkdir()
    if ready_file is not None:
        (directory / ready_file).touch()


def prep_run_sync(
    directory,
    create_ready_file=None,
    check_ready_file=None,
    tar="y",
    untar="y",
    create_dest="y",
):
    source_dir, dest_dir = prep_sync(
        directory,
        create_ready_file=create_ready_file,
        check_ready_file=check_ready_file,
        tar=tar,
        untar=untar,
        create_dest=create_dest,
    )
    run_sync(source_dir)
    return source_dir, dest_dir


def prep_sync(
    directory,
    create_ready_file=None,
    check_ready_file=None,
    tar="y",
    untar="y",
    create_dest="y",
):
    directory = Path(directory)
    source_dir, dest_dir = prep_directories(directory)
    create_test_files(source_dir, ready_file=create_ready_file)
    create_conf_file(
        source_dir,
        dest_dir,
        ready_file=check_ready_file,
        tar=tar,
        untar=untar,
        create_dest=create_dest,
    )
    return source_dir, dest_dir


def run_sync(source_dir):
    sys.argv = ["synchro", str(source_dir), "--no-permission-change"]
    synchro_run()
