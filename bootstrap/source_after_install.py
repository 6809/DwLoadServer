# coding: utf-8

# imports not really needed and just for the editor warning ;)
import sys
import subprocess
import os


def after_install(options, home_dir):
    # --- CUT here ---
    """
    called after virtualenv was created and pip/setuptools installed.
    Now we installed requirement libs/packages.
    """

    raise NotImplementedError("TODO!!!") # TODO


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

    cmd = [self.pip_cmd, "install", "--log=%s" % self.logfile, pip_line]
    subprocess.call(cmd, **self.subprocess_defaults)