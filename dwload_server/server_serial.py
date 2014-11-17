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

from dwload_server.server_base import DwLoadServer, BaseServer


try:
    import serial
except ImportError as err:
    raise ImportError("%s - Please install PySerial ! - http://pyserial.sourceforge.net" % err)

try:
    import dragonlib
except ImportError as err:
    raise ImportError("dragonlib from https://github.com/jedie/DragonPy is needed: %s" % err)

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

        self.sock.settimeout(10)
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
            sys.stderr.write("\nERROR: Can't open serial %r !\n" % port)
            sys.stderr.write("\nRight Port? Port not in use? User rights ok?\n")
            sys.stderr.write(
                "Look at http://archive.worldofdragon.org/index.php?title=Dragon_32/64_Drivewire_Adapter for help!\n")
            sys.stderr.write("\n(Origin error is: %s)\n\n" % err)
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
        log.debug("\thex: %s", " ".join(["$%02x" % b for b in data]))
        return data

    def write(self, data):
        log.debug("WRITE %i:", len(data))
        if LOG_DEZ:
            log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join(["$%02x" % b for b in data]))
        self.conn.write(data)


def run_serial_server(root_dir, port):
    dwload_server = SerialServer(port=port, root_dir=root_dir)
    dwload_server.serve_forever()


if __name__ == '__main__':
    print("\nDirect run, only for testing!", file=sys.stderr)
    print("Please use cli!\n", file=sys.stderr, flush=True)

    sys.argv += [
        "--root_dir=~/dwload-files", "--log_level=10",
        "serial"
    ]
    if sys.platform.startswith('win'):
        sys.argv.append("--port=COM3")
    else:
        sys.argv.append("--port=/dev/ttyUSB0")


    from dwload_server.dwload_server_cli import DwLoadServerCLI
    cli = DwLoadServerCLI()
    cli.run()

    print(" --- END --- ")
