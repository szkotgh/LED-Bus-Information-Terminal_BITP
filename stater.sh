#!bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd -P )"

# Get the path of the script
echo BITP Path=\'$DIR\'
cd "$DIR"

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "BITP Stater must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

# Start the server
sudo python3 app.py