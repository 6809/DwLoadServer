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


class DwHooks:
    def __init__(self):
        self.request_start_hooks = []
        self.pre_hooks = {}
        self.post_hooks = {}

    def register_pre_hook(self, op_code, func):
        log.debug("Add %r to pre %r hook", func.__name__, constants.CODE2NAME[op_code])
        self.pre_hooks.setdefault(op_code, []).append(func)

    def register_post_hook(self, op_code, func):
        log.debug("Add %r to post %r hook", func.__name__, constants.CODE2NAME[op_code])
        self.post_hooks.setdefault(op_code, []).append(func)

    def register_request_start_hook(self, func):
        log.debug("Add %r to RequestStart hook", func.__name__)
        self.request_start_hooks.append(func)

    def _call_hooks(self, hooks, name, hook_type, *args, **kwargs):
        for func in hooks:
            log.debug("Call %s %s hook %r", name, hook_type, func.__name__)
            result = func(*args, **kwargs)
            if result is not None:
                log.debug("hook returned content, skip rest hooks.")
                return result

    def _call_hook_dict(self, d, op_code, hook_type, *args, **kwargs):
        try:
            hooks = d[op_code]
        except KeyError:
            return # There are no hooks for this OP

        return self._call_hooks(hooks, repr(constants.CODE2NAME[op_code]), hook_type, *args, **kwargs)

    def call_request_start_hooks(self, *args, **kwargs):
        return self._call_hooks(self.request_start_hooks, "RequestStart", "start", *args, **kwargs)

    def call_post(self, op_code, *args, **kwargs):
        return self._call_hook_dict(self.post_hooks, op_code, "post", *args, **kwargs)
        
    def call_pre(self, op_code, *args, **kwargs):
        return self._call_hook_dict(self.pre_hooks, op_code, "pre", *args, **kwargs)



DW_HOOKS = DwHooks()


def register_pre_hook(op_code):
    def inner(func):
        DW_HOOKS.register_pre_hook(op_code, func)
        return func
    return inner

def register_post_hook(op_code):
    def inner(func):
        DW_HOOKS.register_post_hook(op_code, func)
        return func
    return inner

def register_request_start_hook():
    def inner(func):
        DW_HOOKS.register_request_start_hook(func)
        return func
    return inner


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