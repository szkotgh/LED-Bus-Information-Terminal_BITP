# BIT Program PATH
DIR="$( cd "$( dirname "$0" )" && pwd -P )"
echo BIT Program Path=\'$DIR\'

if [ $(id -u) -ne 0 ]; then
	echo "BIT Stater must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

cd $DIR
sudo python3 app.py