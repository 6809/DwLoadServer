#!/bin/bash

#
# Startup helper script for DWLOAD-Server
#
# Put this file into root directoy of the created virtual environment
# e.g.:
#     ~/dwload_server_env/start_becker_DWLOAD_server.sh
#
##############################################################################
# Edit this for your needs:
ROOT_DIR=~/dwload-files/

# Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL
LOG_LEVEL=20

# Must normaly not changed:
IP="127.0.0.1"
PORT=65504
##############################################################################

(
    # Activate the virtualenv
    source bin/activate

    while true
    do
        clear
        echo "Run DWLOAD-Server with Becker Interface"
        echo " * root dir: ${ROOT_DIR}"
        echo " * listen on ${IP}:${PORT}"
        echo
        (
            set -x
            python3 -m dwload_server.dwload_server_cli --root_dir=${ROOT_DIR} --log_level=${LOG_LEVEL} becker --ip=${IP} --port=${PORT}
        )
        echo
        read -n1 -p "Press any key to restart" __
        echo
    done
)