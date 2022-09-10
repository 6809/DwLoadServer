"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import logging
import sys

import serial

from dwload_server.server_base import BaseServer, DwLoadServer


LOG_DEZ = False

log = logging.getLogger(__name__)


class SerialServer(BaseServer):
    def __init__(self, port, *args, **kwargs):
        self.port = port
        self.conn = serial.Serial()

        self.dwload_server = DwLoadServer(self, *args, **kwargs)

        self.conn.port = port
        self.conn.baudrate = 57600
        try:
            self.conn.open()
        except serial.serialutil.SerialException as err:
            sys.stderr.write(f"\nERROR: Can't open serial {port!r} !\n")
            sys.stderr.write("\nRight Port? Port not in use? User rights ok?\n")
            sys.stderr.write(
                "Look at http://archive.worldofdragon.org/index.php?title=Dragon_32/64_Drivewire_Adapter for help!\n")
            sys.stderr.write(f"\n(Origin error is: {err})\n\n")
            sys.exit(-1)

        log.debug("Settings for serial %r:", self.conn.name)
        settings = self.conn.getSettingsDict()
        for k, v in sorted(settings.items()):
            log.debug("\t%15s : %s", k, v)

    def serve_forever(self):
        while True:
            try:
                self.dwload_server.serve_forever()
            finally:
                log.critical("Finally: Close serial connection.")
                self.conn.close()

    def read(self, size=1):
        log.debug("READ %i:", size)
        data = self.conn.read(size)
        if LOG_DEZ:
            log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join([f"${b:02x}" for b in data]))
        return data

    def write(self, data):
        log.debug("WRITE %i:", len(data))
        if LOG_DEZ:
            log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join([f"${b:02x}" for b in data]))
        self.conn.write(data)


def run_serial_server(root_dir, port):
    dwload_server = SerialServer(port=port, root_dir=root_dir)
    dwload_server.serve_forever()
