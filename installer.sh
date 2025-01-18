#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd -P )"
CMDLINE_FILE="/boot/firmware/cmdline.txt"
RULES_FILE="/etc/udev/rules.d/99-usb-serial.rules"
RULE_CONTENT='KERNEL=="ttyUSB[0-9]*", MODE="0666", OWNER="root", GROUP="root"'

# Get the path of the script
echo BITP Program Path=\'$DIR\'
cd "$DIR"

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "BITP Installer must be run as root."
    echo "Try 'sudo bash $0'"
    exit 1
fi

echo "This BITP_Installer will reboot after execution."
echo -n "Do you want to continue? [y/[n]] "
read -r REPLY
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
    echo "Exit by refusing reboot."
    exit 1
fi

# install module
{
    sudo apt install python3-pip &&
    sudo python3 -m pip config set global.break-system-packages true &&
    sudo python -m pip install --upgrade pip &&
    sudo pip install --upgrade setuptools &&
    echo "Installing requirement python modules..." &&
    sudo pip install -r requirements.txt
} || {
    echo "BITP installation failed."
    exit 1
}
echo "Python modules installed successfully."
echo

# Install service
{
    echo "Installing service..." &&
    $DIR/src/service_regi.sh
} || {
    echo "BITP installation failed."
    exit 1
}
echo "Service registered successfully."
echo

# Add isolcpus=3 option to cmdline.txt
{
    if grep -q "isolcpus=3" "$CMDLINE_FILE"; then
        echo "isolcpus=3 option already exists."
    else
        echo "Adding isolcpus=3 option to $CMDLINE_FILE..." &&
        sed -i 's/$/ isolcpus=3/' "$CMDLINE_FILE" &&
        echo "isolcpus=3 option added successfully."
    fi
} || {
    echo "BITP installation failed."
    exit 1
}
echo

# install rgb matrix installer
{
    echo "Installing RGB Matrix..." &&
    bash $DIR/src/rgb-matrix_installer.sh &&
    rm -rf $DIR/rpi-rgb-led-matrix
} || {
    echo "BITP installation failed."
    exit 1
}
echo "RGB Matrix installation completed successfully."
echo

# Add udev rule for USB serial
{
    echo "$RULE_CONTENT" | sudo tee "$RULES_FILE" > /dev/null &&
    sudo udevadm control --reload-rules &&
    sudo udevadm trigger
} || {
    echo "An error occurred during the udev rule setup process"
    exit 1
}

# complete installation
echo "BITP installation completed successfully."
echo

# reboot
for ((i=5; i>=1; i--)); do
    echo "Reboot in $i seconds..."
    sleep 1
done
echo "Reboot process started."
reboot now