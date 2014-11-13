# coding: utf-8


# imports not really needed and just for the editor warning ;)
import os
import sys
import subprocess


# Will be inserted in real bootstrap file ;)
DEVELOPER_INSTALLATION=None
NORMAL_INSTALLATION=None


# --- CUT here ---

# For choosing the installation type:
INST_PYPI="pypi"
INST_GIT="git_readonly"
INST_DEV="dev"

INST_TYPES=(INST_PYPI, INST_GIT, INST_DEV)
