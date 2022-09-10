"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/
OP_NOP = 0x00
OP_NAMEOBJ_MOUNT = 0x01
OP_NAMEOBJ_CREATE = 0x02
OP_READ_EXTENDED = 0xd2
OP_WRITE = 0x57

CODE2NAME = {  # A little hackish?
    v: f"{k} ${v:02x}" for k, v in locals().copy().items() if k.startswith("OP")
}

if __name__ == '__main__':
    print(CODE2NAME)
