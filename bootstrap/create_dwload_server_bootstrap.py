#!/usr/bin/env python
# coding: utf-8

import os
import pprint
import pip
from bootstrap_env import create_bootstrap

REQ_FILENAMES=(
    "normal_installation.txt",
    "git_readonly_installation.txt",
    "developer_installation.txt",
)

BASE_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__)))

PREFIX_SCRIPT=os.path.abspath(os.path.join(BASE_PATH, "source_prefix_code.py"))

REQ_BASE_PATH=os.path.abspath(os.path.join(BASE_PATH, "..", "requirements"))
print("requirement files path: %r" % REQ_BASE_PATH)


def get_requirements(filepath):
    requirements=pip.req.parse_requirements(filepath)
    entries = []
    for req in requirements:
        entry = req.url or req.name
        print("\t* %r" % entry)
        entries.append(entry)
    print()
    return entries


def requirements_definitions():
    content = []
    for filename in REQ_FILENAMES:
        print("requirements from %r:" % filename)
        content.append("\n# requirements from %s" % filename)
        requirements_list = get_requirements(filepath=os.path.join(REQ_BASE_PATH, filename))
        req_type = os.path.splitext(filename)[0].upper()
        content.append(
            "%s = %s" % (req_type, pprint.pformat(requirements_list))
        )

    return "\n".join(content)



if __name__ == '__main__':
    prefix_code = "\n".join([
        requirements_definitions(),
        create_bootstrap.get_code(PREFIX_SCRIPT, create_bootstrap.INSTALL_PIP_MARK),
    ])

    create_bootstrap.generate_bootstrap(
        out_filename=os.path.join("..", "boot_dwload_server.py"),
        add_extend_parser="source_extend_parser.py",
        add_adjust_options="source_adjust_options.py",
        add_after_install="source_after_install.py",
        cut_mark="# --- CUT here ---",
        prefix=prefix_code, # Optional code that will be inserted before extend_parser() code part.
        suffix=None, # Optional code that will be inserted after after_install() code part.
    )