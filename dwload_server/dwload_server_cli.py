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
import logging
import os
import textwrap
import sys

from dragonlib.utils.logging_utils import setup_logging, LOG_LEVELS

from dwload_server import __version__
from dwload_server.server_becker import run_becker_server
from dwload_server.server_serial import run_serial_server

log = logging.getLogger(__name__)

class RootDirAction(argparse.Action):
    """ Just use os.path.expanduser() for the path. """
    def __call__(self, parser, namespace, values, option_string=None):
        values = os.path.expanduser(values)
        setattr(namespace, self.dest, values)


class DwLoadServerCLI(object):
    def __init__(self):
        print("\nDWLOAD Server written in Python (GNU GPL v3+) v%s\n" % __version__)

        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.parser.epilog = textwrap.dedent(
            '''
            example usage:
                {prog} --root_dir=./dwload-files/ serial --port=/dev/ttyUSB0
                {prog} --root_dir=./dwload-files/ becker
    
            Interface help:
                {prog} serial --help
                {prog} becker --help
            '''.format(prog=self.parser.prog)
        )
        self.parser.add_argument('--version', action='version',
            version='%%(prog)s %s' % __version__
        )

        self.parser.add_argument(
            '--root_dir', dest='root_dir', action=RootDirAction,
            help="Server root directory for load/store requested files"
        )
        self.parser.add_argument(
            '--log_level', dest="log_level", type=int,
            choices=LOG_LEVELS, default=logging.INFO,
            help="Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL"
        )

        self.sub_parsers = self.parser.add_subparsers(title="Interface")

        # Run with Becker interface:

        self.parser_becker = self.sub_parsers.add_parser(name="becker",
            help="Use the Becker interface",
            # epilog="e.g.: '%s --machine CoCo2b' run" % self.parser.prog
        )
        self.parser_becker.set_defaults(func=self.run_becker_server)

        self.parser_becker.add_argument(
            '--ip', dest='ip', required=True, default="127.0.0.1",
            help="Port number, default: 127.0.0.1",
        )
        self.parser_becker.add_argument(
            '--port', dest='port', type=int, required=True, default=65504,
            help="Port number, default: 65504",
        )

        # Run with Serial interface:

        self.parser_serial = self.sub_parsers.add_parser(name="serial",
            help="Use the serial interface",
            # epilog="e.g.: '%s --machine CoCo2b' run" % self.parser.prog
        )
        self.parser_serial.set_defaults(func=self.run_serial_server)

        self.parser_serial.add_argument(
            '--port', dest='port', required=True,
            help="Serial port. Windows e.g.: 'COM3' - Linux e.g.: '/dev/ttyUSB0'"
        )

    def run(self):
        self.args = self.parser.parse_args()
        setup_logging(level=self.args.log_level)

        log.debug("run func: %s", self.args.func.__name__)
        self.args.func()

    def run_becker_server(self):
        run_becker_server(self.args.root_dir, ip=self.args.ip, port=self.args.port)

    def run_serial_server(self):
        run_serial_server(self.args.root_dir, port=self.args.port)


if __name__ == '__main__':
    cli = DwLoadServerCLI()
    cli.run()

    print(" --- END --- ")