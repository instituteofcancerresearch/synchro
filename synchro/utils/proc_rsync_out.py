# Dictionaries based on description here:
# https://stackoverflow.com/a/36851784/21297098

update_dict = {
    ".": "Item is not being updated..............................",
    "<": "New item to be sent to the remote host.................",
    ">": "New item to be received by the local host..............",
    "c": "Local change to / creation of item (e.g. dir, link)....",
    "h": "Hard link detected.....................................",
    "*": "Itemized output contains a message.....................",
}

type_dict = {
    "f": "file.......",
    "d": "directory..",
    "L": "symlink....",
    "D": "device.....",
    "S": "special....",
}


def parse_line(line):
    """
    Parse line from rsync itemized output,
    to determine whether transfer needs to take place
    e.g.

    >f+++++++++ path/to/new/file
    .f...p..... path/to/old/file/with/diff/permissions

    This latter case is relatively unimportant
    if we have transferred with changing permissions!

    We don't want to tar a massive directly and send
    this just to redo the permission change upon receipt.
    """

    bit_positions, filename = line.split(" ")

    update_bit, type_bit, *other_bits = bit_positions

    update_desc = update_dict[update_bit]
    type_desc = type_dict[type_bit]

    output_message = f"{update_desc} : {type_desc} : {filename}"

    # TODO: Formulate better methods from user end to make these decisions.
    #  Currently just ignores . bits
    return False if update_bit == "." else True, output_message
