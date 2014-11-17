# encoding:utf-8

"""
    DwLoadServer - A DWLOAD server written in Python
    ================================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DwLoadServer team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import time
import logging
import os

from dragonlib.api import Dragon32API
from dwload_server import constants


log = logging.getLogger(__name__)


class DwHooks(object):
    def __init__(self):
        self.pre_hooks = {}
        self.post_hooks = {}

    def register_pre_hook(self, op_code, func):
        log.debug("Add %r to pre %r hook", func.__name__, constants.CODE2NAME[op_code])
        self.pre_hooks.setdefault(op_code, []).append(func)

    def register_post_hook(self, op_code, func):
        self.post_hooks.setdefault(op_code, []).append(func)

    def call_post(self, op_code, *args, **kwargs):
        try:
            hooks = self.post_hooks[op_code]
        except KeyError:
            return # There are no hooks for this OP
        for func in hooks:
            log.debug("Call %r post hook %r", constants.CODE2NAME[op_code], func.__name__)
            func(*args, **kwargs)


DW_HOOKS = DwHooks()


def register_post_hook(op_code):
    def inner(func):
        DW_HOOKS.register_post_hook(op_code, func)
        return func

    return inner


# class SaveASCII(object):
# def __init__(self):
#         self.filepath=None
#
#     def set_filepath(self, filepath):
#         log.debug("Set filepath: %r", filepath)
#         self.filepath = filepath
#
#     def post_write(self, filepath, lsn)
#
# save_ascii=SaveASCII()
#
#
# @register_post_hook(constants.OP_NAMEOBJ_MOUNT)
# def save_ascii_post_mount_hook(server, filename, drive_number):
#     log.critical("Hook info: Filename %r attached to drive number: %i", filename, drive_number)
#     filepath = os.path.join(server.root_dir, filename)
#     save_ascii.set_filepath(filepath)

def backup_rename(filepath):
    """
    renamed filepath if it's a existing file by expand filename with last modified time

    :param filepath: source file that should be renamed
    :return:
    """
    if os.path.isfile(filepath):
        log.info("Create a backup of the old %r", filepath)

        mtime = os.path.getmtime(filepath)
        mtime = time.localtime(mtime)

        bak_filepath = filepath + time.strftime("-%Y%m%d-%H%M%S")
        if not os.path.isfile(bak_filepath + ".bak"):
            bak_filepath += ".bak"
        else:
            count = 1
            while os.path.isfile(bak_filepath + "-%01i.bak" % count):
                count += 1
            bak_filepath += "-%01i.bak" % count

        os.rename(filepath, bak_filepath)
        log.info("Backup as: %r", bak_filepath)


@register_post_hook(constants.OP_WRITE)
def save_ascii_post_write_hook(server, filepath, lsn):
    log.critical("Hook info: Filepath %r LSN: %i", filepath, lsn)

    # TODO: Optimize this:
    with open(filepath, "rb") as f:
        content = f.read()
    if not content.endswith(b"\x00\x00\x00"):
        log.info("File ends not with $00 $00 $00, ok.")
        return

    log.info("File end found. Parse binary...")

    api = Dragon32API()

    ascii_listing = api.bin2bas(content)

    bas_filepath = filepath + ".bas"
    backup_rename(bas_filepath)

    log.info("Create %r...", bas_filepath)
    with open(bas_filepath, "w") as f:
        f.write("\n".join(ascii_listing))


if __name__ == '__main__':
    from dragonlib.utils.logging_utils import setup_logging

    setup_logging(
        level=1 # hardcore debug ;)
        #         level=10  # DEBUG
        #         level=20  # INFO
        #         level=30  # WARNING
        #         level=40 # ERROR
        #         level=50 # CRITICAL/FATAL
        #         level=99
    )

    filepath = os.path.expanduser("~/dwload-files/AUTOLOAD.DWL")

    backup_rename(filepath)
    backup_rename(filepath)
    backup_rename(filepath)