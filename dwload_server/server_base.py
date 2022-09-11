"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging
import math
import os
import struct
import sys
from pathlib import Path

from dragonlib.utils.byte_word_values import word2bytes

from dwload_server import constants
from dwload_server.exceptions import DwException, DwNotReadyError, DwReadError, DwWriteError
from dwload_server.utils.hook_handler import DW_HOOKS


log = logging.getLogger(__name__)
root_logger = logging.getLogger()

LOG_DEZ = False


def drivewire_checksum(data):
    """
    http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/#appendix-b-drivewire-checksum-algorithm
    """
    checksum = 0
    for b in data:
        checksum += b
    return checksum


def print_bytes(bytes):
    for item in bytes:
        if isinstance(item, int):
            item = chr(item)
        if item.isalnum():
            sys.stdout.write(item.decode("ascii"))
        else:
            sys.stdout.write(f" ${ord(item):02x} ")
        sys.stdout.flush()


class DwLoadServer:
    """
    The DWLOAD server
    """

    def __init__(self, interface, root_dir: Path):
        self.interface = interface
        assert isinstance(root_dir, Path)
        self.root_dir = root_dir
        log.info("Root directory is: %r", self.root_dir)
        if not self.root_dir.is_dir():
            raise NotADirectoryError(self.root_dir)

        # FIXME: Import for register and import it here, after logging init:
        import dwload_server.hooks.dynamic_dwl
        import dwload_server.hooks.read_ascii
        import dwload_server.hooks.save_ascii

        self.drive_number = 256
        self.file_info = {}

    def handle_filename(self):
        byte_count, content = self.interface.read_block()
        filename = "".join([chr(i) for i in content])

        self.drive_number -= 1
        self.file_info[self.drive_number] = filename

        log.info("Filename %r attached to drive number: %i", filename, self.drive_number)
        self.interface.write_byte(self.drive_number)

        DW_HOOKS.call_post(constants.OP_NAMEOBJ_MOUNT, self, filename, self.drive_number)

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

        lsn = self.interface.read_integer(size=3)  # Read "Logical Sector Number" (24 bit value)
        log.debug("Logical Sector Number (LSN): $%02x (dez.: %i) ", lsn, lsn)

        return filepath, lsn

    def read_extended_transaction(self):
        self.filepath, lsn = self.get_filepath_lsn()

        chunk = DW_HOOKS.call_pre(constants.OP_READ_EXTENDED, self, self.filepath, lsn)
        if chunk is not None:
            log.info("Use chunk from pre hook.")
        else:
            log.info("Send chunk of file %r", self.filepath)
            try:
                with open(self.filepath, "rb") as f:
                    filesize = os.fstat(f.fileno()).st_size
                    chunk_count = math.ceil(filesize / 256)
                    log.debug("Filesize: %i Bytes == %i * 256 Bytes chunks", filesize, chunk_count)

                    pos = 256 * lsn
                    log.debug("\tseek to: %i", pos)
                    f.seek(pos)
                    log.debug("\tread 256 bytes")
                    chunk = f.read(256)  # TODO: padding to 256 bytes
            except OSError as err:
                raise DwReadError(err)

        self.interface.write(chunk)

        checksum = drivewire_checksum(chunk)
        log.info("Calculated checksum: $%x dez: %i", checksum, checksum)
        bytes = word2bytes(checksum)
        log.critical(repr(bytes))

        try:
            client_checksum = self.interface.read_integer(size=2)  # 16bit checksum calculated by Dragon
        except:
            pass
        else:
            log.debug("TODO: compare checksum: $%04x (dez.: %i)", client_checksum, client_checksum)

        self.interface.write_byte(0x00)  # confirm checksum

        log.debug(" *** block send.")

    def write_transaction(self):
        self.filepath, lsn = self.get_filepath_lsn()

        DW_HOOKS.call_pre(constants.OP_WRITE, self, self.filepath, lsn)

        if lsn == 0:
            mode = "wb"
        else:
            mode = "r+b"

        log.info("Save chunk with %r to: %r", mode, self.filepath)
        chunk = self.interface.read(size=256)

        try:
            with open(self.filepath, mode) as f:
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

        client_checksum = self.interface.read_integer(size=2)  # 16bit checksum calculated by Dragon
        log.debug("TODO: compare checksum: $%04x (dez.: %i)", client_checksum, client_checksum)

        self.interface.write_byte(0x00)  # confirm checksum

        DW_HOOKS.call_post(constants.OP_WRITE, self, self.filepath, lsn)

        log.debug(" *** block written in file.")

    def serve_forever(self):
        log.debug("Serve forever")
        while True:
            req_type = self.interface.read_byte()
            log.debug("Request type: $%02x", req_type)
            try:
                # http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/#transaction-op_nameobj_mount
                if req_type == constants.OP_NOP:  # $00
                    log.debug(" *** NOP Transaction -> ignored ***")
                elif req_type == constants.OP_NAMEOBJ_MOUNT:  # $01 - dez.: 1
                    log.debug(" *** mount name object: ***")
                    self.handle_filename()
                elif req_type == constants.OP_NAMEOBJ_CREATE:  # $02 - dez.: 2
                    log.debug(" *** create name object: ***")
                    self.handle_filename()
                elif req_type == constants.OP_READ_EXTENDED:  # $d2 - dez.: 210
                    log.debug(" *** Read Extended Transaction: ***")
                    self.read_extended_transaction()
                elif req_type == constants.OP_WRITE:  # $57 - dez.: 87
                    log.debug(" *** Write Transaction: ***")
                    self.write_transaction()
                else:
                    msg = "Request type $%02x (dez.: %i) is not supported, yet." % (
                        req_type,
                        req_type,
                    )
                    if root_logger.level <= 10:
                        raise NotImplementedError(msg)
                    log.error(msg)
                    self.interface.write_byte(0x00)

            except DwException as err:
                if root_logger.level <= 10:
                    raise
                sys.exit()
                log.error(err)
                log.debug("Send DW error code $%02x back.", err.ERROR_CODE)
                self.interface.write_byte(err.ERROR_CODE)


class BaseServer:
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
