def create_conf_file(
    source_dir, dest_dir, ready_file=None, filename="synchro.conf"
):
    conf_file = source_dir / filename
    with open(conf_file, "w") as f:
        f.write(f"destination = {dest_dir}\n")
        f.write("untar = y\n")
        f.write("create_dest = y\n")

        if ready_file is not None:
            f.write(f"transfer_ready_file = {ready_file}\n")
