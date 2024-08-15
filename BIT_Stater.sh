#!/bin/bash

if [ $(id -u) -ne 0 ]; then
    echo "BIT Stater must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

DIR="$( cd "$( dirname "$0" )" && pwd -P )"
echo BIT Program Path=\'$DIR\'
cd $DIR

# install module
sudo apt install python3-xmltodict
sudo apt install python3-dotenv

# Replace the current shell with the python3 process
sudo python3 app.py
