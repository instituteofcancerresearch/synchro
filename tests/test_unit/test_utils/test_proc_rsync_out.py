from synchro.utils import proc_rsync_out


def test_parse_line_new():
    assert proc_rsync_out.parse_line(">f+++++++++ path/to/new/file")[0] is True
    assert (
        proc_rsync_out.parse_line(
            ".f...p..... path/to/old/file/with/diff/permissions"
        )[0]
        is False
    )
