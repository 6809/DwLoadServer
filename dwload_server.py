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
import sys
import struct
import math

try:
    import serial
except ImportError as err:
    raise ImportError("%s - Please install PySerial ! - http://pyserial.sourceforge.net" % err)

log = logging.getLogger(__name__)


def print_settings(ser):
    print("Settings for serial %r:" % ser.name)
    settings = ser.getSettingsDict()
    for k, v in sorted(settings.items()):
        print("%20s : %s" % (k, v))
    sys.stdout.flush()


def print_bytes(bytes):
    for item in bytes:
        if isinstance(item, int):
            item = chr(item)
        if item.isalnum():
            sys.stdout.write(item.decode("ascii"))
        else:
            sys.stdout.write(" $%02x " % ord(item))
        sys.stdout.flush()


class DebugSerial(serial.Serial):
    def read(self, size=1):
        log.debug("READ %i:", size)
        data = super(DebugSerial, self).read(size)
        log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join(["$%02x" % b for b in data]))
        return data

    def write(self, data):
        log.debug("WRITE %i:", len(data))
        log.debug("\tdez: %s", " ".join(["%i" % b for b in data]))
        log.debug("\thex: %s", " ".join(["$%02x" % b for b in data]))
        super(DebugSerial, self).write(data)


class DwLoadServer(object):
    def __init__(self, root_dir):
        self.root_dir = os.path.normpath(root_dir)
        log.info("Root directory is: %r", self.root_dir)
        # self.ser = serial.Serial()
        self.ser = DebugSerial()

        self.drive_number = 256
        self.file_info = {}

    def connect(self, port):
        self.ser.port = port
        self.ser.baudrate = 57600
        self.ser.open()
        print_settings(self.ser)

    def read_byte(self):
        raw_byte = self.ser.read(1)
        return struct.unpack("B", raw_byte)[0]

    def read_bytes(self, size):
        raw_byte = self.ser.read(size)
        return struct.unpack("B" * size, raw_byte)

    def read_integer(self, size):
        raw_byte = self.ser.read(size)
        integers = struct.unpack("B" * size, raw_byte)
        result = sum(integers)
        log.debug("read %i Bit integer: %s = %i", size * 8, repr(integers), result)
        return result

    def write_byte(self, value):
        raw_byte = struct.pack("B", value)
        self.ser.write(raw_byte)

    def read_block(self):
        byte_count = self.read_byte()
        log.debug("Read block with a length of %i", byte_count)
        content = self.ser.read(byte_count)
        return byte_count, content

    def handle_filename(self):
        byte_count, content = self.read_block()
        filename = "".join([chr(i) for i in content])

        self.drive_number -= 1
        self.file_info[self.drive_number] = filename

        log.debug("Filename %r attached to drive number: %i", byte_count, self.drive_number)
        self.write_byte(self.drive_number)

    def read_extended_transaction(self):
        drive_number = self.read_byte()
        log.debug("Drive Number: $%02x (dez.: %i)", drive_number, drive_number)

        filename = self.file_info[drive_number]
        filepath = os.path.join(self.root_dir, filename)
        log.debug("Filename %r path: %r", filename, filepath)

        lsn = self.read_integer(size=3) # Read "Logical Sector Number" (24 bit value)
        log.debug("Logical Sector Number (LSN): $%02x (dez.: %i) ", lsn, lsn)

        with open(filepath, "rb") as f:
            filesize = os.fstat(f.fileno()).st_size
            chunk_count = math.ceil(filesize / 256)
            log.debug("Filesize: %i Bytes == %i * 256 Bytes chunks", filesize, chunk_count)

            pos = 256 * lsn
            log.debug("\tseek to: %i", pos)
            f.seek(pos)
            log.debug("\tread 256 bytes")
            chunk = f.read(256) # TODO: padding to 256 bytes

        self.ser.write(chunk)

        client_checksum = self.read_integer(size=2) # 16bit checksum calculated by Dragon
        log.debug("TODO: compare checksum: $%04x (dez.: %i)", client_checksum, client_checksum)

        self.write_byte(0x00) # confirm checksum

        log.debug(" *** block send.")


    def write_transaction(self):
        drive_number = self.read_byte()
        log.debug("Drive Number: $%02x (dez.: %i)", drive_number, drive_number)

        filename = self.file_info[drive_number]
        filepath = os.path.join(self.root_dir, filename)
        log.debug("Filename %r path: %r", filename, filepath)

        lsn = self.read_integer(size=3) # Read "Logical Sector Number" (24 bit value)
        log.debug("Logical Sector Number (LSN): $%02x (dez.: %i) ", lsn, lsn)

        log.debug("Request chunk data to write:")
        chunk = self.ser.read(size=256)
        with open(filepath, "ab") as f:
            pos = 256 * lsn
            log.debug("\tseek to: %i", pos)
            f.seek(pos)
            log.debug("\twrite %i bytes", len(chunk))
            f.write(chunk)
            f.flush()
            filesize = os.fstat(f.fileno()).st_size
        log.debug("Filesize now: %i", filesize)

        client_checksum = self.read_integer(size=2) # 16bit checksum calculated by Dragon
        log.debug("TODO: compare checksum: $%04x (dez.: %i)", client_checksum, client_checksum)

        self.write_byte(0x00) # confirm checksum

        log.debug(" *** block written in file.")

    def serve_forever(self):
        log.debug("Serve forever")
        while True:
            req_type = self.read_byte()
            log.debug("Request type: $%02x", req_type)
            if req_type == 0x01:
                log.debug(" *** handle filename: ***")
                self.handle_filename()

            elif req_type == 0xd2: # dez.: 210
                log.debug(" *** Read Extended Transaction: ***")
                self.read_extended_transaction()

            elif req_type == 0x57: # dez.: 87
                log.debug(" *** Write Transaction: ***")
                self.write_transaction()

            else:
                raise NotImplementedError("Request type $%02x (dez.: %i) is not supported, yet." % (
                    req_type, req_type
                ))


if __name__ == '__main__':
    from utils.logging_utils import setup_logging

    setup_logging(
        # level=1 # hardcore debug ;)
        level=10  # DEBUG
        # level=20  # INFO
        # level=30  # WARNING
        # level=40 # ERROR
        #         level=50 # CRITICAL/FATAL
    )

    dwload = DwLoadServer(root_dir="dwload-demo-files")

    # TODO: Put in ~/config.ini ?!?
    if sys.platform == 'win32':
        port = "COM3"
    else:
        port = "/dev/ttyUSB0"

    dwload.connect(port)
    dwload.serve_forever()

    print(" --- END --- ")
