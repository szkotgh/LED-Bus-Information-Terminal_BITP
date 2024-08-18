#!/bin/bash

# Check if the script is running as root
if [ $(id -u) -ne 0 ]; then
    echo "BITP Stater must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

# Get the path of the script
DIR="$( cd "$( dirname "$0" )" && pwd -P )"
echo BITP Program Path=\'$DIR\'
cd $DIR

# Start the BITP program without sudo
python3 bitp_app.py
