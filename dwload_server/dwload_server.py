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
import socket
import sys
import struct
import math


try:
    import serial
except ImportError as err:
    raise ImportError("%s - Please install PySerial ! - http://pyserial.sourceforge.net" % err)

try:
    import dragonlib
except ImportError as err:
    raise ImportError("dragonlib from https://github.com/jedie/DragonPy is needed: %s" % err)

from dragonlib.api import Dragon32API as Api
from dragonlib.utils.logging_utils import setup_logging, LOG_LEVELS

LOG_DEZ=False

log = logging.getLogger(__name__)



# http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/#appendix-a-error-codes

class DwException(BaseException):
    pass
    # def __init__(self, message):
    #     self.message = message
    #     log.error(message)
    #     log.debug("Send DW error code $%02x back.", self.ERROR_CODE)
    #     ser.write_byte(self.ERROR_CODE)


class DwCrcError(DwException):
    """ CRC Error (if the Server’s computed checksum doesn’t match a write request from the Dragon/CoCo) """
    ERROR_CODE = 0xF3 # dez.: 243

class DwReadError(DwException):
    """ Read Error (if the Server encounters an error when reading a sector from a virtual drive) """
    ERROR_CODE = 0xF4 # dez.: 244

class DwWriteError(DwException):
    """ Write Error (if the Server encounters an error when writing a sector) """
    ERROR_CODE = 0xF5 # dez.: 245

class DwNotReadyError(DwException):
    """ Not Ready Error (if the a command requests accesses a non- existent virtual drive) """
    ERROR_CODE = 0xF6 # dez.: 246



def drivewire_checksum(data):
    """
    http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/#appendix-b-drivewire-checksum-algorithm
    """
    checksum = 0
    for b in data:
        checksum += b
    return checksum




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


class SerialInterface(object):
    def __init__(self):
        self.conn = serial.Serial()
            
    def connect(self, port):
        self.conn.port = port
        self.conn.baudrate = 57600
        try:
            self.conn.open()
        except serial.serialutil.SerialException as err:
            sys.stderr.write("\nERROR: Can't open serial %r !\n" % port)
            sys.stderr.write("\nRight Port? Port not in use? User rights ok?\n")
            sys.stderr.write("Look at http://archive.worldofdragon.org/index.php?title=Dragon_32/64_Drivewire_Adapter for help!\n")
            sys.stderr.write("\n(Origin error is: %s)\n\n" % err)
            sys.exit(-1)
        print_settings(self.ser)

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



class DwLoadServer(object):
    """
    The DWLOAD server
    """
    def __init__(self, interface, root_dir, log_level):
        self.interface = interface
        self.root_dir = os.path.normpath(root_dir)
        log.info("Root directory is: %r", self.root_dir)
        self.log_level=log_level

        self.drive_number = 256
        self.file_info = {}

    def handle_filename(self):
        byte_count, content = self.interface.read_block()
        filename = "".join([chr(i) for i in content])

        self.drive_number -= 1
        self.file_info[self.drive_number] = filename

        log.info("Filename %r attached to drive number: %i", filename, self.drive_number)
        self.interface.write_byte(self.drive_number)

    def get_filepath_lsn(self):
        drive_number = self.interface.read_byte()
        log.debug("Drive Number: $%02x (dez.: %i)", drive_number, drive_number)

        try:
            filename = self.file_info[drive_number]
        except KeyError:
            raise DwNotReadyError(
                "Drive number %i unknown. Existing IDs: %s", drive_number, ",".join(self.file_info.keys())
            )

        filepath = os.path.join(self.root_dir, filename)
        log.debug("Filename %r path: %r", filename, filepath)

        lsn = self.interface.read_integer(size=3) # Read "Logical Sector Number" (24 bit value)
        log.debug("Logical Sector Number (LSN): $%02x (dez.: %i) ", lsn, lsn)

        return filepath, lsn

    def read_extended_transaction(self):
        filepath, lsn = self.get_filepath_lsn()

        log.info("Send chunk of file %r", filepath)
        try:
            with open(filepath, "rb") as f:
                filesize = os.fstat(f.fileno()).st_size
                chunk_count = math.ceil(filesize / 256)
                log.debug("Filesize: %i Bytes == %i * 256 Bytes chunks", filesize, chunk_count)

                pos = 256 * lsn
                log.debug("\tseek to: %i", pos)
                f.seek(pos)
                log.debug("\tread 256 bytes")
                chunk = f.read(256) # TODO: padding to 256 bytes
        except OSError as err:
            raise DwReadError(err)

        self.interface.write(chunk)

        checksum = drivewire_checksum(chunk)
        log.info("Calculated checksum: $%x dez: %i", checksum, checksum)
        bytes = word2bytes(checksum)
        log.critical(repr(bytes))

        try:
            client_checksum = self.interface.read_integer(size=2) # 16bit checksum calculated by Dragon
        except:
            pass
        else:
            log.debug("TODO: compare checksum: $%04x (dez.: %i)", client_checksum, client_checksum)

        self.interface.write_byte(0x00) # confirm checksum

        log.debug(" *** block send.")


    def write_transaction(self):
        filepath, lsn = self.get_filepath_lsn()

        log.info("Save chunk to: %r", filepath)
        chunk = self.interface.read(size=256)
        try:
            with open(filepath, "ab") as f:
                pos = 256 * lsn
                log.debug("\tseek to: %i", pos)
                f.seek(pos)
                log.debug("\twrite %i bytes", len(chunk))
                f.write(chunk)
                f.flush()
                filesize = os.fstat(f.fileno()).st_size
        except OSError as err:
            raise DwWriteError(err)

        log.debug("Filesize now: %i", filesize)

        checksum = drivewire_checksum(chunk)
        log.info("Calucated checksum: $%x dez: %i", checksum, checksum)

        client_checksum = self.interface.read_integer(size=2) # 16bit checksum calculated by Dragon
        log.debug("TODO: compare checksum: $%04x (dez.: %i)", client_checksum, client_checksum)

        self.interface.write_byte(0x00) # confirm checksum

        log.debug(" *** block written in file.")

    def serve_forever(self):
        log.debug("Serve forever")
        while True:
            req_type = self.interface.read_byte()
            log.debug("Request type: $%02x", req_type)
            try:
                if req_type == 0x01: # dez.: 1 - ransaction OP_NAMEOBJ_MOUNT
                    # http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/#transaction-op_nameobj_mount
                    log.debug(" *** handle filename: ***")
                    self.handle_filename()

                # TODO: 0x02 for "SAVE"

                elif req_type == 0xd2: # dez.: 210
                    log.debug(" *** Read Extended Transaction: ***")
                    self.read_extended_transaction()

                elif req_type == 0x57: # dez.: 87
                    log.debug(" *** Write Transaction: ***")
                    self.write_transaction()

                else:
                    msg="Request type $%02x (dez.: %i) is not supported, yet." % (
                        req_type, req_type
                    )
                    # raise NotImplementedError(msg)
                    log.error(msg)
                    self.interface.write_byte(0x00)
            except DwException as err:
                log.error(err)
                log.debug("Send DW error code $%02x back.", err.ERROR_CODE)
                self.interface.write_byte(err.ERROR_CODE)


class BaseServer(object):
    def read_byte(self):
        raw_byte = self.read(1)
        return struct.unpack("B", raw_byte)[0]

    def read_bytes(self, size):
        raw_byte = self.read(size)
        return struct.unpack("B" * size, raw_byte)

    def read_integer(self, size):
        raw_byte = self.read(size)
        integers = struct.unpack(">" + "B" * size, raw_byte)
        result = sum(integers)
        log.debug("read %i Bit integer: %s = %i", size * 8, repr(integers), result)
        return result

    def write_byte(self, value):
        raw_byte = struct.pack("B", value)
        self.write(raw_byte)

    def read_block(self):
        byte_count = self.read_byte()
        log.debug("Read block with a length of %i", byte_count)
        content = self.read(byte_count)
        return byte_count, content


class BeckerServer(BaseServer):
    def __init__(self, ip="127.0.0.1", port=65504, *args, **kwargs):
        self.ip=ip
        self.port=port

        self.dwload_server = DwLoadServer(self, *args, **kwargs)

        log.critical("Listen for incoming connections on %s:%s ...", self.ip, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(1)

    def serve_forever(self):
        while True:
            log.critical("Waiting for a connection on %s:%s ...", self.ip, self.port)
            self.conn, client_address = self.sock.accept()
            log.critical("Incoming connection from %r", client_address)

            try:
                self.dwload_server.serve_forever()
            except ConnectionError as err:
                log.error("ERROR: %s", err)

    def read(self, size=1):
        log.debug("READ %i:", size)
        data = self.conn.recv(size)
        if len(data)!=size:
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


def start_server(root_dir, port, log_level=logging.INFO):
    setup_logging(level=log_level)

    dwload = DwLoadServer(root_dir=root_dir, log_level=log_level)
    dwload.connect(port)
    dwload.serve_forever()



def cli():
    # TODO: serial/becker
    parser = argparse.ArgumentParser(
        description="DWLOAD Server written in Python (GNU GPL v3+)"
        #epilog="foo"
    )

    parser.add_argument(
        '--port', dest='port', required=True,
        help="Serial port. Windows e.g.: 'COM3' - Linux e.g.: '/dev/ttyUSB0'"
    )
    parser.add_argument(
        '--root_dir', dest='root_dir', required=True,
        help="Directory for load/store requested files, e.g.: 'dwload-demo-files'"
    )
    parser.add_argument(
        '--log_level', dest="log_level", type=int, choices=LOG_LEVELS, default=logging.INFO,
        help="Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL"
    )

    args = parser.parse_args()

    start_server(
        root_dir=args.root_dir,
        port=args.port,
        log_level=args.log_level
    )



if __name__ == '__main__':
    # cli()

    root_dir=os.path.expanduser("~/workspace/DWLOAD/dwload-demo-files")
    log_level=logging.DEBUG
    setup_logging(level=log_level)

    dwload_server=BeckerServer(
        ip="127.0.0.1", port=65504,
        root_dir=root_dir, log_level=log_level
    )
    dwload_server.serve_forever()

    print(" --- END --- ")
