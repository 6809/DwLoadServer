#!/usr/bin/env python

"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import argparse
import datetime
import logging
import os
import string
import sys


try:
    import dragonlib
except ImportError as err:
    raise ImportError(f"dragonlib from https://github.com/jedie/DragonPy is needed: {err}")

from dragonlib.api import Dragon32API
from dragonlib.utils.logging_utils import LOG_LEVELS, setup_logging

from dwload_server.utils.file_tools import fnmatch_case_insensitve2, padding


log = logging.getLogger(__name__)

SKIP_PATTERN = (
    "*.asm", "*.txt", "*.py", "*.bak",
    "*.BAS.dwl", # own created files

    "AUTOLOAD.DWL",
)

SELECT_KEYS = string.digits + string.ascii_uppercase

def generate_basic(path):
    log.info("Generate AUTOLOAD.DWL for directory %r...", path)

    select_keys = SELECT_KEYS.replace("XYZ", "") # remove

    dir_info = []
    index = 0
    for item in sorted(os.listdir(path)):
        if fnmatch_case_insensitve2(item, SKIP_PATTERN):
            log.info("Skip %r, ok.", item)
            continue

        abs_path = os.path.join(path, item)

        # TODO: Support directories!
        if os.path.isdir(abs_path):
            log.error("Skip %r TODO: Support directories!", item)
            continue

        # TODO: filter filename with unsupported characters

        if not os.path.isfile(abs_path):
            log.info("Skip %r, not a file, ok.", item)
            continue

        try:
            select_key = select_keys[index]
        except IndexError:
            log.error("Dir has more than %i entries! Skip the rest :(", len(SELECT_KEYS))
            break
        dir_info.append(
            (index, select_key, item)
        )
        index += 1
        log.debug(item)

    listing = [
        "10 CLS",
        f"20 PRINT\" *** DYNAMIC MENU ***  {datetime.datetime.now().strftime('%H:%M:%S')}\"",
        f'30 PRINT"{path.upper()}"',
    ]
    line_no = 30
    for entry in dir_info:
        line_no += 10
        listing.append(f'{line_no} PRINT" {entry[1]} - {entry[2]}"')
        # log.debug(entry)

    line_no += 10
    listing.append(f'{line_no} PRINT"PLEASE SELECT (X FOR RELOAD) !"')
    line_no += 10
    listing.append(
        '{lineno} A$=INKEY$:IF A$="" GOTO {lineno}'.format(
            lineno=line_no
        )
    )
    line_no += 10
    listing.append(f'{line_no} IF A$="X" THEN DLOAD')

    for entry in dir_info:
        line_no += 10
        listing.append(f'{line_no} IF A$="{entry[1]}" THEN DLOAD"{entry[2]}"')
        log.debug(entry)

    line_no += 10
    listing.append(f'{line_no} GOTO 10')

    return "\n".join(listing)


def get_content(path, print_listing):
    """
    Only a DEMO, doesn't do really fancy stuff.
    Just read the existing AUTOLOAD.DWL and return the bytes...
    """
    log.info("Create AUTOLOAD.DWL 'on-the-fly'...")

    basic_program_ascii = generate_basic(path)

    if print_listing:
        print(basic_program_ascii, file=sys.stderr)

    api = Dragon32API()

    data = api.bas2bin(basic_program_ascii,
        # FIXME:
        load_address=0x1e01, exec_address=0x1e01 # from example
    )

    log.debug("size before padding: %i Bytes", len(data))
    data = padding(data, size=256, b=b"\x00")
    log.debug("size after padding: %i Bytes", len(data))

    return data


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log_level', dest="log_level", type=int, choices=LOG_LEVELS, default=logging.INFO,
        help="Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL"
    )
    parser.add_argument('--filepath', dest="filepath", required=True)
    args = parser.parse_args()

    setup_logging(level=args.log_level)

    log.debug("Given path: %r", args.filepath)
    path = os.path.split(args.filepath)[0]

    if args.log_level <= 10:
        print_listing = True
    else:
        print_listing = False

    content = get_content(path, print_listing)
    log.debug("Send %i Bytes back so server process.", len(content))
    sys.stdout.buffer.write(content)


def test_run(path):
    setup_logging(level=logging.DEBUG)
    log.critical("\n\n *** DISABLE THIS TEST RUN !!! *** \n")
    content = get_content(path, print_listing=True)


if __name__ == '__main__':
    cli()
    # test_run(os.path.expanduser("~/dwload-files")) # Only for developing!

