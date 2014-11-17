# encoding:utf-8

"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import logging
import socket
import sys
import time

try:
    import serial
except ImportError as err:
    raise ImportError("%s - Please install PySerial ! - http://pyserial.sourceforge.net" % err)

try:
    import dragonlib
except ImportError as err:
    raise ImportError("dragonlib from https://github.com/jedie/DragonPy is needed: %s" % err)

from dwload_server.server_base import BaseServer, DwLoadServer
from dragonlib.utils.logging_utils import setup_logging


LOG_DEZ = False

log = logging.getLogger(__name__)


class BeckerServer(BaseServer):
    def __init__(self, ip="127.0.0.1", port=65504, *args, **kwargs):
        self.ip = ip
        self.port = port

        self.dwload_server = DwLoadServer(self, *args, **kwargs)

        log.critical("Listen for incoming connections on %s:%s ...", self.ip, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(1)

        self.sock.settimeout(60)
        log.debug("Socket timeout: %r", self.sock.gettimeout())

    def serve_forever(self):
        while True:
            log.critical("Waiting for a connection on %s:%s ...", self.ip, self.port)
            self.conn, client_address = self.sock.accept()
            log.critical("Incoming connection from %r", client_address)

            try:
                self.dwload_server.serve_forever()
            except ConnectionError as err:
                log.error("ERROR: %s", err)

    def recv_all(self, size):
        buf = []
        while size > 0:
            data = self.conn.recv(size)
            if data:
                log.debug("\tReceive %i Bytes", len(data))
            buf.append(data)
            size -= len(data)
            if size > 0:
                time.sleep(0.1)
        return b''.join(buf)

    def read(self, size=1):
        log.debug("READ %i:", size)
        data = self.recv_all(size)
        if len(data) != size:
            log.error("Receive %i Bytes, but %i are expected!", len(data), size)

        if LOG_DEZ:
            log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join(["$%02x" % b for b in data]))
        return data

    def write(self, data):
        log.debug("WRITE %i:", len(data))
        if LOG_DEZ:
            log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join(["$%02x" % b for b in data]))
        self.conn.sendall(data)


def run_becker_server(root_dir, ip="127.0.0.1", port=65504):
    dwload_server = BeckerServer(ip=ip, port=port, root_dir=root_dir)
    dwload_server.serve_forever()


if __name__ == '__main__':
    print("\nDirect run, only for testing!", file=sys.stderr)
    print("Please use cli!\n", file=sys.stderr, flush=True)

    sys.argv += [
        "--root_dir=~/dwload-files", "--log_level=10",
        "becker", "--ip=127.0.0.1", "--port=65504"
    ]

    from dwload_server.dwload_server_cli import DwLoadServerCLI
    cli = DwLoadServerCLI()
    cli.run()

    print(" --- END --- ")
