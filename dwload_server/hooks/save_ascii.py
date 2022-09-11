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
from dwload_server.utils.file_tools import backup_rename, rename_with_backup, fnmatch_case_insensitve


log = logging.getLogger(__name__)


class SaveFilenames:
    def __init__(self, filepath):
        self.basefilepath = os.path.splitext(filepath)[0]
        self.dwl_filepath = self.basefilepath + ".DWL"
        self.bas_filepath = self.basefilepath + ".BAS"


@hook_handler.register_pre_hook(constants.OP_WRITE)
def save_ascii_pre_write_hook(server, filepath, lsn):
    """
    Just backup all files, before overwrite them
    """
    if lsn != 0:
        log.debug("Not LSN==0: Do no file backup.")
        return

    backup_rename(filepath)

    if fnmatch_case_insensitve(filepath, "*.BAS"):
        filenames = SaveFilenames(filepath)
        backup_rename(filenames.bas_filepath)
        backup_rename(filenames.dwl_filepath)


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

    log_hexlines(content, msg=f"{os.path.basename(filepath)} data:", level=logging.DEBUG)

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

    filenames = SaveFilenames(filepath)

    # Rename existing file (created by server) to foo.DWL
    rename_with_backup(filepath, filenames.dwl_filepath)

    # Create up-to-date .BAS file
    log.info("Save ASCII Listing to %r...", filenames.bas_filepath)
    with open(filenames.bas_filepath, "w") as f:
        f.write(ascii_listing)