#!/bin/bash

(
    set -x
    python3 -m dwload_server.dwload_server --port /dev/ttyUSB0 --root_dir ./root
)
echo
read -n1 -p "Start bash? [y,n]" doit
echo
case $doit in
    y|Y)
        bash -i
        exit 0
        ;;
    n|N)
        echo "bye bye"
        ;;
    *)
        echo "input, don't know, bye."
        ;;
esac