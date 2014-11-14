#!/usr/bin/env python
# encoding:utf-8

"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import argparse
import os
import logging
import sys

try:
    import dragonlib
except ImportError as err:
    raise ImportError("dragonlib from https://github.com/jedie/DragonPy is needed: %s" % err)

from dragonlib.utils.logging_utils import setup_logging, LOG_LEVELS


log = logging.getLogger(__name__)


def get_content():
    """
    Only a DEMO, doesn't do really fancy stuff.
    Just read the existing AUTOLOAD.DWL and return the bytes...
    """
    log.info("Create AUTOLOAD.DWL 'on-the-fly'...")

    filepath = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "AUTOLOAD.DWL"
    ))
    log.debug("Open %r...", filepath)
    with open(filepath, "rb") as f:
        content = f.read()

    log.debug("%i bytes readed.", len(content))

    return content


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log_level', dest="log_level", type=int, choices=LOG_LEVELS, default=logging.INFO,
        help="Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL"
    )
    args = parser.parse_args()

    setup_logging(level=args.log_level)

    content = get_content()
    sys.stdout.buffer.write(content)


if __name__ == '__main__':
    cli()