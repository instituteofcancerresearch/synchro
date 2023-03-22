import logging


def create_conf_file(
    source_dir,
    dest_dir,
    ready_file=None,
    filename="synchro.conf",
    tar="y",
    untar="y",
    create_dest="y",
    email_address="person@place.com",
    email_on_start="n",
    email_on_end="n",
    transfer_ongoing_file_exists=False,
    persistent_log_file=False,
):
    conf_file = source_dir / filename
    with open(conf_file, "w") as f:
        f.write(f"source = {source_dir}\n")
        f.write(f"destination = {dest_dir}\n")
        f.write(f"tar = {tar}\n")
        f.write(f"untar = {untar}\n")
        f.write(f"create_dest = {create_dest}\n")
        f.write(f"email_address = {email_address}\n")
        f.write(f"email_on_start = {email_on_start}\n")
        f.write(f"email_on_end = {email_on_end}\n")

        if ready_file is not None:
            f.write(f"transfer_ready_file = {ready_file}\n")

    return conf_file


def setup_simple_log(filename, file_level="DEBUG"):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, file_level))
    fh = logging.FileHandler(filename)
    fh.setLevel(getattr(logging, file_level))
    logger.addHandler(fh)
