"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os

from dwload_server.utils.file_tools import backup_rename, padding, fnmatch_case_insensitve
from dragonlib.api import Dragon32API
from dwload_server import constants
from dwload_server.utils import hook_handler
from dragonlib.utils.logging_utils import log_hexlines


log = logging.getLogger(__name__)


def change_filepath(server, new_filepath):
    # FIXME: Hackish!
    old_filepath = server.filepath
    log.info("Change filename from %r to %r", old_filepath, new_filepath)
    server.filepath = new_filepath


@hook_handler.register_pre_hook(constants.OP_READ_EXTENDED)
def read_ascii_read_pre_hook(server, filepath, lsn):
    if not fnmatch_case_insensitve(filepath, "*.BAS"):
        log.info("Don't convert to Dragon DOS Binary: No .BAS file, ok")
        return

    dwl_filepath = filepath + ".dwl"

    if lsn != 0:
        if os.path.isfile(dwl_filepath):
            change_filepath(server, dwl_filepath)
        return

    # We read the first sector of the last requested filepath

    log.info("Read ASCII listing from %r...", filepath)
    with open(filepath) as f:
        basic_program_ascii = f.read()

    api = Dragon32API()

    data = api.bas2bin(basic_program_ascii,
        # FIXME:
        load_address=0x1e01, exec_address=0x1e01 # from example AUTOLOAD.DWL
    )
    
    log.debug("size before padding: %i Bytes", len(data))
    log_hexlines(data, msg="before padding")

    data = padding(data, size=256, b=b"\x00")

    log_hexlines(data, msg="after padding")
    log.debug("size after padding: %i Bytes", len(data))

    backup_rename(dwl_filepath)
    with open(dwl_filepath, "wb") as f:
        f.write(data)

    change_filepath(server, dwl_filepath)


if __name__ == "__main__":
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(
        # level=1 # hardcore debug ;)
        level=10  # DEBUG
        # level=20  # INFO
        #         level=30  # WARNING
        #         level=40 # ERROR
        #         level=50 # CRITICAL/FATAL
    )

    filepath = os.path.expanduser("~/dwload-files/FOO.BAS")
    with open(filepath) as f:
        basic_program_ascii = f.read()

    api = Dragon32API()

    data = api.bas2bin(basic_program_ascii,
        # FIXME:
        load_address=0x1e01, exec_address=0x1e01 # from example
    )

    log.debug("size before padding: %i Bytes", len(data))
    data = padding(data, size=256, b=b"\x00")
    log.debug("size after padding: %i Bytes", len(data))

    log.debug(repr(data))

    print(" --- END --- ")