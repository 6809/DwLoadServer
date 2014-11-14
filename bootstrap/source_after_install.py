# coding: utf-8

# imports not really needed and just for the editor warning ;)
import sys
import subprocess
import os
from bootstrap.source_prefix_code import (
    INST_PYPI, INST_GIT, INST_DEV,
    NORMAL_INSTALLATION,GIT_READONLY_INSTALLATION,DEVELOPER_INSTALLATION
)

def after_install(options, home_dir):
    # --- CUT here ---
    """
    called after virtualenv was created and pip/setuptools installed.
    Now we installed requirement libs/packages.
    """

    abs_home_dir = os.path.abspath(home_dir)
    logfile = os.path.join(abs_home_dir, "install.log")
    bin_dir = os.path.join(abs_home_dir, "bin")
    python_cmd = os.path.join(bin_dir, "python")
    pip_cmd = os.path.join(bin_dir, "pip")
    
    subprocess_defaults = {
        "cwd": bin_dir,
        "env": {
            "VIRTUAL_ENV": home_dir,
            "PATH": bin_dir + ":" + os.environ["PATH"],
        }
    }

    if options.install_type==INST_PYPI:
        requirements=NORMAL_INSTALLATION
    elif options.install_type==INST_GIT:
        requirements=GIT_READONLY_INSTALLATION
    elif options.install_type==INST_DEV:
        requirements=DEVELOPER_INSTALLATION
    else:
        raise RuntimeError("Install type %r unknown?!?" % options.install_type) # Should never happen

    for requirement in requirements:
        cmd = [pip_cmd, "install", "--log=%s" % logfile, requirement]
        sys.stdout.write("\n+ %s\n" % " ".join(cmd))
        subprocess.call(cmd, **subprocess_defaults)
        sys.stdout.write("\n")