#!/usr/bin/env python
# encoding:utf-8

"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import logging
import subprocess
import sys

try:
    import dragonlib
except ImportError as err:
    raise ImportError("dragonlib from https://github.com/jedie/DragonPy is needed: %s" % err)

from dragonlib.utils.logging_utils import setup_logging


log = logging.getLogger(__name__)


def get_pyscript_stdout(filepath, log_level=10, timeout=3):
    script_file = "%s.py" % filepath

    if not os.path.isfile(script_file):
        log.debug("PyScript %r doesn't exist, ok.", script_file)
        return None

    log.info("%r exists.", script_file)

    cmd = [sys.executable, script_file, "--log_level=%i" % log_level]
    log.debug("Call: %s" % " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=sys.stderr)
    try:
        outs, errs = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        log.error("ERROR: script timeout %i arrived :(", timeout)
        proc.kill()
        outs, errs = proc.communicate()

    log.info("%i Bytes received from pyscript.", len(outs))

    return outs


if __name__ == '__main__':
    print("\nTest run!\n")

    setup_logging(
        # level=1 # hardcore debug ;)
        level=10  # DEBUG
        #         level=20  # INFO
        #         level=30  # WARNING
        #         level=40 # ERROR
        #         level=50 # CRITICAL/FATAL
    )

    content = get_pyscript_stdout(
        filepath=os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "dwload-demo-files", "AUTOLOAD.DWL"
        ))
    )
    print("returned content: %s" % repr(content))