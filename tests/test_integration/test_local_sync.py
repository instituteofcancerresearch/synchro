import os
import sys
from pathlib import Path
from synchro.cli import main as synchro_run
from ..utils.utils import create_conf_file

TEST_FILES = ("test1.txt", "test2.txt")
TEST_DIRS = ("test_dir",)


def test_not_sync_in_progress(tmpdir):
    # Initial run produces transfer done file
    src_dir, dest_dir, config_file = prep_and_run_sync(
        tmpdir, in_progress_file="transfer.ongoing"
    )
    assert not dest_dir.exists()


def test_local_sync_4_files(tmpdir):
    # Run without creating or requiring a ready file
    _, dest_dir, _ = prep_and_run_sync(tmpdir)

    # num files + dirs + 1 for conf file
    assert (
        len(list(dest_dir.iterdir())) == len(TEST_DIRS) + len(TEST_FILES) + 1
    ), os.listdir(dest_dir)


def test_local_sync_no_untar(tmpdir):
    # Run without untar
    _, dest_dir, _ = prep_and_run_sync(tmpdir, untar="n")

    # just tar ball on transfer end
    assert len(list(dest_dir.iterdir())) == 1


def test_local_sync_no_tar(tmpdir):
    # Run without tar
    _, dest_dir, _ = prep_and_run_sync(tmpdir, tar="n")

    # num files + dirs + 1 for conf file
    assert (
        len(list(dest_dir.iterdir())) == len(TEST_DIRS) + len(TEST_FILES) + 1
    ), os.listdir(dest_dir)


def test_local_sync_5_files(tmpdir, ready_file="ready.txt"):
    # Create a ready file, but do not require it
    _, dest_dir, _ = prep_and_run_sync(tmpdir, create_ready_file=ready_file)

    # num files + dirs + 1 for conf + 1 for ready file
    assert (
        len(list(dest_dir.iterdir()))
        == len(TEST_DIRS) + len(TEST_FILES) + 1 + 1
    ), os.listdir(dest_dir)


def test_conditional_local_sync(tmpdir, ready_file="ready.txt"):
    # Create a ready file, and require it
    _, dest_dir, _ = prep_and_run_sync(
        tmpdir, create_ready_file=ready_file, check_ready_file=ready_file
    )

    # num files + dirs + 1 for conf + 1 for ready file
    assert (
        len(list(dest_dir.iterdir()))
        == len(TEST_DIRS) + len(TEST_FILES) + 1 + 1
    ), os.listdir(dest_dir)


def test_conditional_local_sync_no_ready_file(tmpdir, ready_file="ready.txt"):
    # Don't create a ready file, and require it
    _, dest_dir, _ = prep_and_run_sync(tmpdir, check_ready_file=ready_file)
    assert dest_dir.exists() is False


def test_skip_with_done_file(tmpdir):
    # Test that transfer is skipped if already performed

    _, dest_dir, config_file = prep_and_run_sync(tmpdir)
    assert dest_dir.exists()

    remove_path(dest_dir)
    sys.argv = ["synchro", str(config_file)]
    synchro_run()
    assert dest_dir.exists() is False


def test_skip_cron_with_done_file(tmpdir):
    # test that transfer is skipped if done file exists in cron mode

    # Initial run produces transfer done file
    src_dir, dest_dir, config_file = prep_and_run_sync(tmpdir)
    assert dest_dir.exists()
    transfer_done_file = src_dir / "transfer.done"

    assert transfer_done_file.exists()
    remove_path(dest_dir)

    # Running again in cron mode should still not work whilst this file exists
    sys.argv = ["synchro", str(config_file), "--cron"]
    synchro_run()
    assert dest_dir.exists() is False


def test_not_done_file_with_cron(tmpdir):
    # test that transfer is repeated if transfer.done file does not exist

    # Initial run produces transfer done file
    src_dir, dest_dir, config_file = prep_and_run_sync(tmpdir)
    assert dest_dir.exists()
    transfer_done_path = src_dir / "transfer.done"

    # Delete transfer done file
    remove_path(transfer_done_path)

    # Check that only
    assert (
        len(list(dest_dir.iterdir())) == len(TEST_FILES) + len(TEST_DIRS) + 1
    ), os.listdir(dest_dir)

    # Rerun synchro in cron mode
    sys.argv = ["synchro", str(config_file), "--cron"]
    synchro_run()
    assert dest_dir.exists() is True
    assert transfer_done_path.exists() is False

    assert (
        len(list(dest_dir.iterdir())) == len(TEST_FILES) + len(TEST_DIRS) + 1
    ), os.listdir(dest_dir)

    # create new file
    (src_dir / "new_file.txt").touch()

    sys.argv = ["synchro", str(config_file), "--cron"]
    synchro_run()
    assert dest_dir.exists() is True
    assert transfer_done_path.exists() is False

    assert (
        len(list(dest_dir.iterdir())) == len(TEST_FILES) + len(TEST_DIRS) + 2
    ), os.listdir(dest_dir)


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


def create_test_files(
    directory, ready_file=None, in_progress_file=None, transfer_done_file=None
):
    for test_file in TEST_FILES:
        (directory / test_file).touch()
    for test_dir in TEST_DIRS:
        (directory / test_dir).mkdir()

    if ready_file is not None:
        (directory / ready_file).touch()
    if in_progress_file is not None:
        (directory / in_progress_file).touch()
    if transfer_done_file is not None:
        (directory / transfer_done_file).touch()


def prep_and_run_sync(
    directory,
    create_ready_file=None,
    check_ready_file=None,
    in_progress_file=None,
    tar="y",
    untar="y",
    create_dest="y",
):
    """
    Prepare source directory, define dest directory
    and consutrct configuration file

    :param create_ready_file: creates transfer ready file in source
    :param check_ready_file: checks whether transfer ready file in source
    :param in_progress_file: creates in progress file whilst transferring
    """
    source_dir, dest_dir, config_file = prep_sync(
        directory,
        create_ready_file=create_ready_file,
        check_ready_file=check_ready_file,
        in_progress_file=in_progress_file,
        tar=tar,
        untar=untar,
        create_dest=create_dest,
    )
    run_sync(config_file)
    return source_dir, dest_dir, config_file


def prep_sync(
    directory,
    create_ready_file=None,
    check_ready_file=None,
    in_progress_file=None,
    transfer_done_file=None,
    tar="y",
    untar="y",
    create_dest="y",
):
    directory = Path(directory)
    source_dir, dest_dir = prep_directories(directory)
    create_test_files(
        source_dir,
        ready_file=create_ready_file,
        in_progress_file=in_progress_file,
        transfer_done_file=transfer_done_file,
    )
    config_file = create_conf_file(
        source_dir,
        dest_dir,
        ready_file=check_ready_file,
        tar=tar,
        untar=untar,
        create_dest=create_dest,
    )
    return source_dir, dest_dir, config_file


def run_sync(config_file):
    sys.argv = ["synchro", str(config_file), "--no-permission-change"]
    synchro_run()
