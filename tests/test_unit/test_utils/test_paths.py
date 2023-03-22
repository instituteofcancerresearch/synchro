from synchro.utils.paths import Paths
from synchro.utils.misc import get_config_obj
from ...utils.utils import create_conf_file


def construct_paths_and_config(tmpdir, log_filename, persistent_log):
    destination = tmpdir / "dest"
    create_conf_file(tmpdir, destination)

    config = get_config_obj(tmpdir / "synchro.conf")

    return Paths(config, log_filename, persistent_log), config


class TestPaths:
    # TODO: think of more robust test for this

    def test_set_source_directory(self, tmpdir):
        paths, config = construct_paths_and_config(tmpdir, None, False)
        assert paths.source_directory.exists()

    def test_set_destination_directory(self, tmpdir):
        paths, config = construct_paths_and_config(tmpdir, None, False)
        assert not paths.destination_directory.exists()

    def test_source_neq_destination(self, tmpdir):
        paths, config = construct_paths_and_config(tmpdir, None, False)
        assert paths.source_directory != paths.destination_directory
