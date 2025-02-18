#!/bin/bash
# Convenient pi-timolo2-install.sh script written by Claude Pageau 1-Jul-2016
ver="13.1"
progName=$(basename -- "$0")
TIMOLO2_DIR='pi-timolo2'  # Default folder install location

# Make sure ver below matches latest rclone ver on https://downloads.rclone.org/rclone-current-linux-arm.zip
rclone_cur_ver="rclone v1.69.1"

cd ~

is_upgrade=false
if [ -d "$TIMOLO_DIR" ] ; then
  STATUS="Upgrade"
  is_upgrade=true
else
  STATUS="New Install"
  mkdir -p $TIMOLO2_DIR
  echo "$STATUS Created Folder $SPEED_DIR"
fi

cd $TIMOLO2_DIR
INSTALL_PATH=$( pwd )
mkdir -p media
mkdir -p supervisor
mkdir -p plugins
mkdir -p rclone-samples

# Remember where this script was launched from
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "
-------------------------------------------------------------
INFO  : $progName $ver  written by Claude Pageau
        $STATUS from https://github.com/pageauc/pi-timolo2
-------------------------------------------------------------
"
echo "Note: config.py will not be overwritten. Updated settings are in config.py.new"

timoloFiles=("menubox.sh" "timolo2.py" "timolo2.sh" "image-stitching" "config.cfg" "strmpilibcam.py" \
"webserver.py" "webserver.sh" "makevideo.sh" "mvleavelast.sh" "strmpilibcam.py")

for fname in "${timoloFiles[@]}" ; do

    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/$fname)

done

wget -O Readme.md -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/Readme.md
wget -O media/webserver.txt -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/webserver.txt

wget -O supervisor/timolo2-cam.conf -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/supervisor/timolo2-cam.conf
wget -O supervisor/timolo2-web.conf -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/supervisor/timolo2-web.conf

wget -q --show-progress -nc https://raw.github.com/pageauc/pi-timolo2/master/source/user_motion_code.py

if [ -f config.py ]; then     # check if local file exists.
    wget -O config.py.new -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/config.py
else
    wget -O config.py -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/config.py
fi

if [ -f video.conf ]; then     # check if local file exists.
    wget -O video.conf.new -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/video.conf
else
    wget -O video.conf -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/video.conf
fi

if [ ! -f rclone-example.sh ] ; then
    wget -O rclone-example.sh -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/plugins/rclone-security-sync-recent.sh
fi

chmod +x *py
chmod -x config*py
chmod -x strmpilibcam.py
chmod +x *sh

echo "copy image-stitching to /usr/local/bin"
chmod +x image-stitching
sudo cp ./image-stitching /usr/local/bin
rm ./image-stitching


# Install plugins if not already installed.  You must delete a plugin file to force reinstall.
echo "INFO  : $STATUS Check/Install pi-timolo2/plugins    Wait ..."

PLUGINS_DIR='plugins'  # Default folder install location

# List of plugin Files to Check
pluginFiles=("__init__.py" "dashcam.py" "secfast.py" "secQTL.py" "secstill.py" \
"secvid.py" "strmvid.py" "shopcam.py" "slowmo.py" "TLlong.py" "TLshort.py" "TLpan.py" "pano.py")

cd $PLUGINS_DIR
for fname in "${pluginFiles[@]}" ; do
  if [ -f $fname ]; then     # check if local file exists.
    echo "INFO  : $fname plugin Found.  Skip Download ..."
  else
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/plugins/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo2/master/source/plugins/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/pi-timolo2/master/source/plugins/$fname"
        fi
    fi
  fi
done
cd ..

# Install rclone samples
echo "INFO  : $STATUS Check/Install pi-timolo2/rclone-samples    Wait ..."
RCLONE_DIR='rclone-samples'  # Default folder install location
# List of plugin Files to Check
rcloneFiles=("Readme.md" "rclone-master.sh" "rclone-mo-copy-videos.sh" "rclone-mo-sync.sh" \
"rclone-mo-sync-lockfile.sh" "rclone-mo-sync-recent.sh" "rclone-tl-copy.sh" "rclone-tl-sync-recent.sh" "rclone-cleanup.sh")

mkdir -p $RCLONE_DIR
cd $RCLONE_DIR
for fname in "${rcloneFiles[@]}" ; do
    wget_output=$(wget -O $fname -q --show-progress https://raw.github.com/pageauc/pi-timolo2/master/source/rclone-samples/$fname)
    if [ $? -ne 0 ]; then
        wget_output=$(wget -O $fname -q https://raw.github.com/pageauc/pi-timolo2/master/source/rclone-samples/$fname)
        if [ $? -ne 0 ]; then
            echo "ERROR : $fname wget Download Failed. Possible Cause Internet Problem."
        else
            wget -O $fname "https://raw.github.com/pageauc/pi-timolo2/master/source/rclone-samples/$fname"
        fi
    fi
done
chmod +x *sh

cd ..

rclone_install=true
if [ -f /usr/bin/rclone ]; then
    /usr/bin/rclone version
    rclone_ins_ver=$( /usr/bin/rclone version | grep rclone )
    if [ "$rclone_ins_ver" == "$rclone_cur_ver" ]; then
        rclone_install=false
    fi
fi

if "$rclone_install" == true ; then
    # Install rclone with latest version
    echo "INFO  : Install Latest Rclone from https://downloads.rclone.org/rclone-current-linux-arm.zip"
    wget -O rclone.zip -q --show-progress https://downloads.rclone.org/rclone-current-linux-arm.zip
    if [ $? -ne 0 ]; then
        wget -O rclone.zip https://downloads.rclone.org/rclone-current-linux-arm.zip
    fi
    echo "INFO  : unzip rclone.zip to folder rclone-tmp"
    unzip -o -j -d rclone-tmp rclone.zip
    echo "INFO  : Install files and man pages"
    cd rclone-tmp
    sudo cp rclone /usr/bin/
    sudo chown root:root /usr/bin/rclone
    sudo chmod 755 /usr/bin/rclone
    sudo mkdir -p /usr/local/share/man/man1
    sudo cp rclone.1 /usr/local/share/man/man1/
    sudo mandb
    cd ..
    echo "INFO  : Deleting rclone.zip and Folder rclone-tmp"
    rm rclone.zip
    rm -r rclone-tmp
    echo "INFO  : /usr/bin/rclone Install Complete"
else
    echo "INFO  : /usr/bin/rclone is Up-To-Date"
fi

echo "INFO  : $STATUS Install pi-timolo2 Dependencies Wait ..."

sudo apt install -yq python3-picamera2
sudo apt install -yq python3-py3exiv2  # Bookworm and later
sudo apt install -yq python3-opencv
sudo apt install -yq python3-pil
sudo apt install -yq python3-dateutil
sudo apt install -yq python3-pantilthat
sudo apt install -yq python3-rpi.gpio
sudo apt install -yq python3-dateutil
sudo apt install -yq supervisor
sudo apt install -yq ffmpeg   # required for Buster and later.
sudo apt install -yq pandoc   # convert markdown to plain text for Readme.md
sudo apt install -yq dos2unix
sudo apt install -yq exiv2    # Buster

cd $TIMOLO2_DIR

dos2unix -q *py
dos2unix -q *sh

echo "INFO  : $STATUS Done Dependencies Install"

# Check if timolo2-install.sh was launched from pi-timolo2 folder
if [ "$DIR" != "$INSTALL_PATH" ]; then
  if [ -f 'timolo2-install.sh' ]; then
    echo "INFO  : $STATUS Cleanup pi-timolo2-install.sh"
    rm timolo2-install.sh
  fi
fi

# cleanup old files from previous versions of install
cleanup_files=("get-pip.py" "gdrive" "install.sh" "makemovie.sh" "makedailymovie.sh" "pancam.py" "pancam.pyc" \
"convid.conf" "convid.conf.orig" "convid.conf.prev" "convid.conf.1" "convid.conf.new" \
"makevideo.conf" "makevideo.conf.orig" "makevideo.conf.prev" "makevideo.conf.1" \
"makevideo.conf.new" "sync.sh" "timolo-install.sh" "rclone-sync-new.sh" "rclone-videos-new.sh")

for fname in "${cleanup_files[@]}" ; do
    if [ -f $fname ] ; then
        echo "INFO  : Delete $fname"
        rm -f $fname
    fi
done

if [ -f /usr/bin/rclone ]; then
    echo "INFO  : $STATUS rclone is installed at /usr/bin/rclone"
    rclone version
else
    echo "ERROR : $STATUS Problem Installing rclone.  Please Investigate"
fi

echo "
-----------------------------------------------
INFO  : $STATUS Complete ver 13.1
-----------------------------------------------
Minimal Instructions:
1 - Run sudo raspi-config Interfacing Options and enable I2C and Pi Camera
    make sure 

2 - It is suggested you run sudo apt-get update and sudo apt-get upgrade
    Reboot RPI if there are significant Raspbian OS system updates.

3 - If config.py already exists then latest file will be config.py.new

4 - If using Bulleye run sudo raspi-config, Interface Options, 3. 
    Make sure camera is NOT in Legacy mode. Test camera. See commands below
	
	sudo raspi-config              % Check System Options Bullseye Only
	libcamera-hello --list-cameras 
	libcamera-still -o sample.jpg  # you should see file if camera is working OK

5 - You will need to create symlinks to enable supervisorctl operation per below.
	This will allow proper operation of menubox.ah

    cd ~/pi-timolo2
    ./timolo.sh install
    ./webserver.sh install
	
6 - To Test Run pi-timolo2 execute the following commands in RPI SSH
    or terminal session. Default is Motion Track On and TimeLapse On

    cd ~/pi-timolo2
    ./timolo2.py

7 - To manage pi-timolo2, Run menubox.sh per commands below

    cd ~/pi-timolo2
    ./menubox.sh

  
    For help See https://github.com/pageauc/pi-timolo2/

    Good Luck Claude ...

Bye"

