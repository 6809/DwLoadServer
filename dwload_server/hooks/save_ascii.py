# encoding:utf-8

"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os

from dragonlib.api import Dragon32API
from dragonlib.utils.logging_utils import log_bytes, log_hexlines

from dwload_server import constants
from dwload_server.utils import hook_handler
from dwload_server.utils.file_tools import backup_rename


log = logging.getLogger(__name__)


@hook_handler.register_post_hook(constants.OP_WRITE)
def save_ascii_post_write_hook(server, filepath, lsn):
    """
    Save a BASIC listing in "Dragon DOS Binary Format" in a ASCII file, too.

    :param server: DwLoadServer() instance
    :param filepath: current filepath of the written chunk
    :param lsn: current "Logical Sector Number" (not really needed here)
    :return: None
    """
    log.critical("Hook info: Filepath %r LSN: %i", filepath, lsn)

    # TODO: Optimize this:
    with open(filepath, "rb") as f:
        content = f.read()

    log_hexlines(content, msg="%s data:" % os.path.basename(filepath), level=logging.DEBUG)

    if not content.endswith(b"\x00\x00\x00"):
        log.info("File ends not with $00 $00 $00, ok.")
        return

    log.info("File end found. Parse binary...")

    api = Dragon32API()

    try:
        ascii_listing = api.bin2bas(content)
    except Exception as err:
        log.error("Can't parse BASIC file: %s", err)
        log.info("content: %s", repr(content))
        return

    log.debug("ASCII Listing:")
    for line in ascii_listing.splitlines(True): # keepends=True
        log.debug(repr(line))

    bas_filepath = filepath + ".bas"
    backup_rename(bas_filepath)

    log.info("Save ASCII Listing to %r...", bas_filepath)
    with open(bas_filepath, "w") as f:
        f.write(ascii_listing)