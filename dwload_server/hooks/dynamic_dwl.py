"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import os
import sys
import subprocess

from dwload_server import constants
from dwload_server.utils import hook_handler


log = logging.getLogger(__name__)
root_logger = logging.getLogger()

CONTENT_BUFFER = None


class PyScriptBuffer:
    def __init__(self):
        self.buffer = None

    def set_filepath(self, filepath):
        self.origin = filepath
        self.pypath = filepath + ".py"

    def clear(self):
        self.buffer = None

    def load(self):
        self.buffer = self.subprocess_call()

    def subprocess_call(self, timeout=3):
        cmd = [sys.executable, self.pypath,
            "--log_level=%i" % root_logger.level,
            f"--filepath={self.origin}",
        ]
        log.debug(f"Call: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=sys.stderr)
        try:
            outs, errs = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            log.error("ERROR: script timeout %i arrived :(", timeout)
            proc.kill()
            outs, errs = proc.communicate()

        byte_count = len(outs)
        log.info("%i Bytes received from pyscript.", byte_count)
        if byte_count == 0:
            return None

        return outs


pyscript_buffer = PyScriptBuffer()


@hook_handler.register_pre_hook(constants.OP_READ_EXTENDED)
def dynamic_dwl_read_pre_hook(server, filepath, lsn):
    pyscript_buffer.set_filepath(filepath)

    if not os.path.isfile(pyscript_buffer.pypath):
        log.info("Python script %r doesn't exists, ok.", pyscript_buffer.pypath)
        pyscript_buffer.clear()
        return

    log.info("Use Python script %r...", pyscript_buffer.pypath)

    if lsn == 0:
        pyscript_buffer.load()

    if pyscript_buffer.buffer is None:
        log.debug("Buffer is None, ok.")
    else:
        pos = 256 * lsn
        return pyscript_buffer.buffer[pos:pos + 256]
