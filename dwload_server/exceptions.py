"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

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