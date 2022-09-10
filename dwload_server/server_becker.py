"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import logging
import socket
import time

from dwload_server.server_base import BaseServer, DwLoadServer


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
        log.debug("\thex: %s", " ".join([f"${b:02x}" for b in data]))
        return data

    def write(self, data):
        log.debug("WRITE %i:", len(data))
        if LOG_DEZ:
            log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join([f"${b:02x}" for b in data]))
        self.conn.sendall(data)


def run_becker_server(root_dir, ip="127.0.0.1", port=65504):
    dwload_server = BeckerServer(ip=ip, port=port, root_dir=root_dir)
    dwload_server.serve_forever()

