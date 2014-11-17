#!/bin/bash

#
# Startup helper script for DWLOAD-Server
#
# Put this file into root directoy of the created virtual environment
# e.g.:
#     ~/dwload_server_env/start_serial_DWLOAD_server.sh
#
##############################################################################
# Edit this for your needs:
ROOT_DIR=~/dwload-files/

# Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL
LOG_LEVEL=20

# More info:
# http://archive.worldofdragon.org/index.php?title=Dragon_32/64_Drivewire_Adapter#Linux
PORT=/dev/ttyUSB0
##############################################################################

(
    # Activate the virtualenv
    source bin/activate

    while true
    do
        clear
        echo "Run DWLOAD-Server with Serial Interface"
        echo " * root dir: ${ROOT_DIR}"
        echo " * serial port: ${PORT}"
        echo
        (
            set -x
            python3 -m dwload_server.dwload_server_cli --root_dir=${ROOT_DIR} --log_level=${LOG_LEVEL} serial --port=${PORT}
        )
        echo
        read -n1 -p "Press any key to restart" __
        echo
    done
)