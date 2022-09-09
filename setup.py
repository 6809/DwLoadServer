#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :copyleft: 2014 by the DWLOAD-Server team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages
import os
import sys

import dwload_server

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


setup(
    name="dwload_server",
    version=dwload_server.__version__,
    py_modules=["dwload_server"],
    provides=["dwload_server"],
    install_requires=[
        "dragonlib", # https://pypi.python.org/pypi/dragonlib/ | https://github.com/6809/dragonlib
        "pyserial", # https://pypi.python.org/pypi/pyserial/
    ],
    author="Jens Diemer",
    author_email="dwload_server@jensdiemer.de",
    description="DWLOAD server implemented in Python",
    keywords="6809 Dragon CoCo DriveWire",
    url="https://github.com/DWLOAD/DwLoadServer",
    license="GPL v3+",
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Emulators",
        "Topic :: Software Development :: Assemblers",
        "Topic :: Software Development :: Testing",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    # test_suite="dwload_server.tests", # or: .../dwload_server $ python3 -m unittest discover
)
