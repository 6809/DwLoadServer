#!/usr/bin/env python

"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os

try:
    import dragonlib
    from dragonlib.api import Dragon32API as Api
except ImportError as err:
    raise ImportError(f"dragonlib from https://github.com/jedie/DragonPy is needed: {err}")


log = logging.getLogger(__name__)

def dwl2bas(infilename, outfilename):
    with open(infilename, "rb") as infile:
        dwl_content = infile.read()

    api=Api()

    api.pformat_program_dump([ord(char) for char in dwl_content])

    tokens=api.token_util.chars2tokens(dwl_content)

    ascii_listing = api.token_util.tokens2ascii(tokens)

    print(ascii_listing)

    # with open(outfilename, "w") as outfile:


if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(
        # level=1 # hardcore debug ;)
        level=10  # DEBUG
        #         level=20  # INFO
        #         level=30  # WARNING
        #         level=40 # ERROR
        #         level=50 # CRITICAL/FATAL
    )

    dwl2bas(
        infilename=os.path.join("dwload-demo-files", "AUTOLOAD.DWL"),
        outfilename=os.path.join("dwload-demo-files", "AUTOLOAD.bas"),
    )