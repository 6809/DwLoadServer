"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import fnmatch

import logging
import os
import time


log = logging.getLogger(__name__)


def padding(data, size, b=b"\x00"):
    quanta, leftover = divmod(len(data), size)
    # Pad the last quantum with zero bits if necessary
    if leftover:
        data += (b * (size - leftover))
    return data


def fnmatch_case_insensitve(filename, pattern):
    return fnmatch.fnmatch(filename.upper(), pattern.upper())


def fnmatch_case_insensitve2(filename, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(filename.upper(), pattern.upper()):
            return True
    return False


def backup_rename(filepath):
    """
    renamed filepath if it's a existing file by expand filename with last modified time

    :param filepath: source file that should be renamed
    """
    if os.path.isfile(filepath):
        log.info("Create a backup of the old %r", filepath)

        mtime = os.path.getmtime(filepath)
        mtime = time.localtime(mtime)

        bak_filepath = filepath + time.strftime("-%Y%m%d-%H%M%S")
        if not os.path.isfile(bak_filepath + ".bak"):
            bak_filepath += ".bak"
        else:
            count = 1
            while os.path.isfile(bak_filepath + "-%01i.bak" % count):
                count += 1
            bak_filepath += "-%01i.bak" % count

        os.rename(filepath, bak_filepath)
        log.info("Backup as: %r", bak_filepath)


def rename_with_backup(old_filepath, new_filepath):
    backup_rename(new_filepath)
    log.info("Rename %r to %r", old_filepath, new_filepath)
    os.rename(old_filepath, new_filepath)


if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(
        level=1 # hardcore debug ;)
        # level=10  # DEBUG
        # level=20  # INFO
        #         level=30  # WARNING
        #         level=40 # ERROR
        #         level=50 # CRITICAL/FATAL
        #         level=99
    )

    filepath = os.path.expanduser("~/dwload-files/AUTOLOAD.DWL")

    backup_rename(filepath)
    backup_rename(filepath)
    backup_rename(filepath)