#!/bin/bash
# This script will run the pi-timolo2.py as a background task
# You will then be able close the terminal session.
# use the edit option and change autostart=true

user="pi"
service_name="$user-timolo2-cam"
conf_file_dir="/home/$user/pi-timolo2/supervisor"
conf_file_name="timolo2-cam.conf"

# webserver.sh ver 13.15 written by Claude Pageau
echo "-----------------------------------------------"
echo "$0 supervisorctl $1"

if [ "$1" = "start" ]; then
    sudo supervisorctl start $service_name
	exit 0

elif [ "$1" = "stop" ]; then
    sudo supervisorctl stop $service_name
	exit 0

elif [ "$1" = "restart" ]; then
    sudo supervisorctl restart $service_name

elif [ "$1" = "status" ]; then
    sudo supervisorctl status all
    exit 0

elif [ "$1" = "edit" ]; then
    sudo nano $conf_file_dir/$conf_file_name
    sudo supervisorctl reread
    sudo supervisorctl update
    echo "Wait ..."
    sleep 4
    sudo supervisorctl status $service_name
    exit 0

elif [ "$1" = "install" ]; then
    # Run this option to initialize supervisor.service
    echo "install: ln -s $conf_file_dir/$conf_file_name /etc/supervisor/conf.d/$conf_file_name"
    sudo ln -s $conf_file_dir/$conf_file_name /etc/supervisor/conf.d/$conf_file_name
    ls -al /etc/supervisor/conf.d
	sudo supervisorctl reread
	sleep 4
    sudo supervisorctl update

elif [ "$1" = "uninstall" ]; then
    sudo supervisorctl stop $service_name
    sleep 4
	echo "rm sudo /etc/supervisor/conf.d/$conf_file_name"
    sudo rm sudo /etc/supervisor/conf.d/$conf_file_name
    ls -al /etc/supervisor/conf.d
    sudo supervisorctl reread
    sleep 4
    sudo supervisorctl update

elif [ "$1" = "upgrade" ]; then
    curl -L https://raw.github.com/pageauc/pi-timolo2/master/source/timolo2-install.sh | bash
    exit 0
else
   echo "
Usage: ./$(basename "$0") [Option]

  Options:
  start        Start supervisor service
  stop         Stop supervisor service
  restart      restart supervisor service
  status       Status of supervisor service
  edit         nano edit $conf_file_dir
  install      Install symbolic link for webserver supervisor service
  uninstall    Uninstall symbolic link for webserver supervisor service
  upgrade      Upgrade pi-timolo2 files from GitHub
  help         Display Usage message and Status

  Example:  ./$(basename "$0") status
"
fi
echo "Wait ...
"
sudo supervisorctl status all
echo "Done
"
