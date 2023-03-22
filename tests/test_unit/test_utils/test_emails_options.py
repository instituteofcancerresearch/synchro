from synchro.utils.misc import get_config_obj
from synchro.utils.options import Options
from ...utils.utils import create_conf_file

EMAIL_ADDRESS = "person@place.com"


def construct_options(
    tmpdir,
    create_dest=True,
    tar=True,
    untar=True,
    permissions=True,
    delete_source_tar=True,
    delete_destination_tar=True,
    owner=None,
    group=None,
    email_address=EMAIL_ADDRESS,
    email_on_start="n",
    email_on_end="n",
):
    destination = tmpdir / "dest"
    create_conf_file(
        tmpdir,
        destination,
        email_on_start=email_on_start,
        email_on_end=email_on_end,
        email_address=email_address,
    )

    config = get_config_obj(tmpdir / "synchro.conf")

    return Options(
        config,
        create_dest=create_dest,
        tar=tar,
        untar=untar,
        permissions=permissions,
        delete_source_tar=delete_source_tar,
        delete_destination_tar=delete_destination_tar,
        owner=owner,
        group=group,
        email_address=email_address,
        email_on_start=email_on_start,
        email_on_end=email_on_end,
    )


class TestOptions:
    def test_no_email_options(self, tmpdir):
        no_email = construct_options(tmpdir)

        assert no_email.email_address == EMAIL_ADDRESS

        assert no_email.email_on_end is False
        assert no_email.email_on_start is False

    def test_email_on_start_options(self, tmpdir):
        start_only = construct_options(tmpdir, email_on_start="y")

        assert start_only.email_address == EMAIL_ADDRESS

        assert start_only.email_on_end is False
        assert start_only.email_on_start is True

    def test_email_on_end_options(self, tmpdir):
        end_only = construct_options(tmpdir, email_on_end="y")

        assert end_only.email_address == EMAIL_ADDRESS

        assert end_only.email_on_end is True
        assert end_only.email_on_start is False
