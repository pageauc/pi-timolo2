#!/usr/bin/env python3
"""
pi-timolo - Raspberry Pi Long Duration Timelapse, Motion Tracking,
with Low Light Capability
written by Claude Pageau Jul-2017 (release 7.x)
This release uses OpenCV to do Motion Tracking.
It requires updated config.py
Oct 2020 Added panoramic pantilt option plus other improvements.
"""
from __future__ import print_function

PROG_VER = "ver 13.07"  # Requires Latest 12.5 release of config.py
__version__ = PROG_VER  # May test for version number at a future time

import os
os.environ["LIBCAMERA_LOG_LEVELS"]="FATAL"
warn_on = False  # Add short delay to review warning messages
my_path = os.path.abspath(__file__)  # Find the full path of this python script
# get the path location only (excluding script name)
base_dir = os.path.dirname(my_path)
base_file_name = os.path.splitext(os.path.basename(my_path))[0]
PROG_NAME = os.path.basename(__file__)
log_file_path = os.path.join(base_dir, base_file_name + ".log")
HORIZ_LINE = "-------------------------------------------------------"
print(HORIZ_LINE)
print(f"{PROG_NAME} {PROG_VER} written by Claude Pageau Feb-2025")
print("python3 Raspberry PI Camera: TI Timelapse, MO Motion Tracking, LO Low Light")
print("Uses libcamera, picamera2 python libraries. Bullseye or Later")
print(HORIZ_LINE)
print("Loading Wait ....")

# import python library modules
import datetime
import sys
import subprocess
import shutil
import glob
import time
import math
from threading import Thread
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
from picamera2 import Picamera2, Preview
from libcamera import controls, Transform
import logging

# Disable picamera2 and libcamera logging. Some DEBUG messages may still appear
logging.getLogger('picamera2').setLevel(logging.CRITICAL)
logging.getLogger('libcamera').setLevel(logging.CRITICAL)

# Attempt to import dateutil
try:
    from dateutil.parser import parse
except ImportError:
    print("WARN : Could Not Import dateutil.parser")
    print("       Disabling TIMELAPSE_START_AT, MOTION_START_AT and VideoStartAt")
    print(
        "       See https://github.com/pageauc/pi-timolo/wiki/Basic-Trouble-Shooting#problems-with-python-pip-install-on-wheezy"
    )
    warn_on = True
    # Disable get_sched_start if import fails for Raspbian wheezy or Jessie
    TIMELAPSE_START_AT = ""
    MOTION_START_AT = ""
    VIDEO_START_AT = ""

# Attempt to import pyexiv2.  Note python3 can be a problem
try:
    # pyexiv2 Transfers image exif data to writeTextToImage
    # For python3 install of pyexiv2 lib
    # See https://github.com/pageauc/pi-timolo/issues/79
    # Bypass pyexiv2 if library Not Found
    import pyexiv2
except ImportError:
    print("WARN  : Could Not Import pyexiv2. Required for Saving Image EXIF meta data")
    print(
        "        If Running under python3 then Install pyexiv2 library for python3 per"
    )
    print("      sudo apt install python3-py3exiv2 -y")
    warn_on = True
except OSError as err:
    print("WARN  : Could Not import python3 pyexiv2 due to an Operating System Error")
    print("        %s" % err)
    print("        Camera images will be missing exif meta data")
    warn_on = True

"""
This is a dictionary of the default settings for pi-timolo.py
If you don't want to use a config.py file these will create the required
variables with default values.  Change dictionary values if you want different
variable default values.
A message will be displayed if a variable is Not imported from config.py.
Note: plugins can override default and config.py values if plugins are
      enabled.  This happens after config.py variables are initialized
"""
default_settings = {
    "CONFIG_FILENAME": "default_settings",
    "CONFIG_TITLE": "pi-timolo2 ver 13.06 Default Settings",
    "PLUGIN_ON": False,
    "PLUGIN_NAME": "shopcam",
    "VERBOSE_ON": True,
    "LOG_TO_FILE_ON": False,
    "DEBUG_ON": False,
    "IMAGE_NAME_PREFIX": "cam1-",
    "IMAGE_WIDTH": 1920,
    "IMAGE_HEIGHT": 1080,
    "IMAGE_FORMAT": ".jpg",
    "IMAGE_JPG_QUAL": 95,
    "IMAGE_ROTATION": None,
    "IMAGE_VFLIP": True,
    "IMAGE_HFLIP": True,
    "IMAGE_GRAYSCALE": False,
    "IMAGE_PREVIEW": False,
    "IMAGE_PIX_AVE_TIMER_SEC": 15,
    "IMAGE_NO_NIGHT_SHOTS": False,
    "IMAGE_NO_DAY_SHOTS": False,
    "IMAGE_SHOW_STREAM": False,
    "STREAM_WIDTH": 320,
    "STREAM_HEIGHT": 240,
    "STREAM_FPS": 20,
    "STREAM_STOP_SEC": 0.7,
    "SHOW_DATE_ON_IMAGE": True,
    "SHOW_TEXT_FONT_SIZE": 18,
    "SHOW_TEXT_BOTTOM": True,
    "SHOW_TEXT_WHITE": True,
    "SHOW_TEXT_WHITE_NIGHT": True,
    "DARK_MAX_EXP_SEC": 6.0,   # picamera V1 default is 6.0 sec. V2 is 10 Sec
    "DARK_START_PXAVE": 32,    # px_ave transition point between dark and light.
    "DARK_GAIN": 6,
    "TIMELAPSE_ON": True,
    "TIMELAPSE_DIR": "media/timelapse",
    "TIMELAPSE_PREFIX": "tl-",
    "TIMELAPSE_START_AT": "",
    "TIMELAPSE_TIMER_SEC": 300,
    "TIMELAPSE_CAM_SLEEP_SEC": 4.0,
    "TIMELAPSE_NUM_ON": True,
    "TIMELAPSE_NUM_RECYCLE_ON": True,
    "TIMELAPSE_NUM_START": 1000,
    "TIMELAPSE_NUM_MAX": 2000,
    "TIMELAPSE_EXIT_SEC": 0,
    "TIMELAPSE_MAX_FILES": 0,
    "TIMELAPSE_SUBDIR_MAX_FILES": 0,
    "TIMELAPSE_SUBDIR_MAX_HOURS": 0,
    "TIMELAPSE_RECENT_MAX": 200,
    "TIMELAPSE_RECENT_DIR": "media/recent/timelapse",
    "MOTION_TRACK_ON": True,
    "MOTION_TRACK_QUICK_PIC_ON": False,
    "MOTION_TRACK_INFO_ON": True,
    "MOTION_TRACK_TIMEOUT_SEC": 0.3,
    "MOTION_TRACK_TRIG_LEN": 75,
    "MOTION_TRACK_MIN_AREA": 100,
    "MOTION_TRACK_QUICK_PIC_BIGGER": 3.0,
    "MOTION_DIR": "media/motion",
    "MOTION_PREFIX": "mo-",
    "MOTION_START_AT": "",
    "MOTION_VIDEO_ON": False,
    "MOTION_VIDEO_FPS": 15,
    "MOTION_VIDEO_WIDTH": 640,
    "MOTION_VIDEO_HEIGHT": 480,
    "MOTION_VIDEO_TIMER_SEC": 10,
    "MOTION_TRACK_MINI_TL_ON": False,
    "MOTION_TRACK_MINI_TL_SEQ_SEC": 20,
    "MOTION_TRACK_MINI_TL_TIMER_SEC": 4,
    "MOTION_TRACK_PANTILT_SEQ_ON": False,
    "MOTION_FORCE_SEC": 3600,
    "MOTION_NUM_ON": True,
    "MOTION_NUM_RECYCLE_ON": True,
    "MOTION_NUM_START": 1000,
    "MOTION_NUM_MAX": 500,
    "MOTION_SUBDIR_MAX_FILES": 0,
    "MOTION_SUBDIR_MAX_HOURS": 0,
    "MOTION_RECENT_MAX": 200,
    "MOTION_RECENT_DIR": "media/recent/motion",
    "MOTION_CAM_SLEEP": 0.7,
    "VIDEO_REPEAT_ON": False,
    "VIDEO_REPEAT_WIDTH": 1280,
    "VIDEO_REPEAT_HEIGHT": 720,
    "VIDEO_DIR": "media/videos",
    "VIDEO_PREFIX": "vid-",
    "VIDEO_START_AT": "",
    "VIDEO_FILE_SEC": 120,
    "VIDEO_SESSION_MIN": 60,
    "VIDEO_FPS": 30,
    "VIDEO_NUM_ON": False,
    "VIDEO_NUM_RECYCLE_ON": False,
    "VIDEO_NUM_START": 100,
    "VIDEO_NUM_MAX": 20,
    "PANTILT_ON": False,
    "PANTILT_IS_PIMORONI": False,
    "PANTILT_HOME": (0, -10),
    "PANTILT_SPEED": 0.5,
    "PANTILT_SEQ_ON": False,
    "PANTILT_SEQ_TIMER_SEC": 600,
    "PANTILT_SEQ_IMAGES_DIR": "media/pantilt_seq",
    "PANTILT_SEQ_IMAGE_PREFIX": "seq-",
    "PANTILT_SEQ_DAYONLY_ON": True,
    "PANTILT_SEQ_RECENT_DIR": "media/recent/pt-seq",
    "PANTILT_SEQ_NUM_MAX": 200,
    "PANTILT_SEQ_NUM_ON": True,
    "PANTILT_SEQ_NUM_START": 1000,
    "PANTILT_SEQ_NUM_RECYCLE_ON": True,
    "PANTILT_SEQ_NUM_MAX": 200,
    "PANTILT_SEQ_STOPS": [
        (90, 10),
        (45, 10),
        (0, 10),
        (-45, 10),
        (-90, 10),
    ],
    "PANO_ON": False,
    "PANO_DAYONLY_ON": True,
    "PANO_TIMER_SEC": 160,
    "PANO_IMAGE_PREFIX": "pano-",
    "PANO_NUM_START": 1000,
    "PANO_NUM_MAX": 10,
    "PANO_NUM_RECYCLE": True,
    "PANO_PROG_PATH": "./image-stitching",
    "PANO_IMAGES_DIR": "./media/pano/images",
    "PANO_DIR": "./media/pano/panos",
    "PANO_CAM_STOPS": [
        (36, 10),
        (0, 10),
        (-36, 10),
    ],
    "SPACE_TIMER_HOURS": 0,
    "SPACE_TARGET_MB": 500,
    "SPACE_MEDIA_DIR": "/home/pi/pi-timolo2/media",
    "SPACE_TARGET_EXT": "jpg",
    "WEB_SERVER_PORT": 8080,
    "WEB_SERVER_ROOT": "media",
    "WEB_PAGE_TITLE": "PI-TIMOLO2 Media",
    "WEB_PAGE_REFRESH_ON": True,
    "WEB_PAGE_REFRESH_SEC": "900",
    "WEB_PAGE_BLANK_ON": False,
    "WEB_IMAGE_HEIGHT": "768",
    "WEB_IFRAME_WIDTH_PERCENT": "70%",
    "WEB_IFRAME_WIDTH": "100%",
    "WEB_IFRAME_HEIGHT": "100%",
    "WEB_MAX_LIST_ENTRIES": 0,
    "WEB_LIST_HEIGHT": "768",
    "WEB_LIST_BY_DATETIME_ON": True,
    "WEB_LIST_SORT_DESC_ON": True,
}

# Check for config.py variable file to import and error out if not found.
config_file_path = os.path.join(base_dir, "config.py")
if os.path.isfile(config_file_path):
    try:
        from config import CONFIG_TITLE
    except ImportError:
        print("\n           --- WARNING ---\n")
        print("pi-timolo2.py ver 13.0 or greater requires updated config.py for custom settings")
        print("copy new config.py per commands below.\n")
        print("    cp config.py config.py.bak")
        print("    cp config.py.new config.py\n")
        print("config.py.bak will contain your previous settings")
        print("The NEW config.py has renamed variable names. If required")
        print("you will need to review previous settings and change")
        print("the appropriate NEW variable names using nano.\n")
        print(
            "Note: ver 12.0 has added a pantilthat panoramic image stitching feature\n"
        )
        print("    Press Ctrl-c to Exit and update config.py")
        print("                      or")
        text = raw_input("    Press Enter and Default Settings will be used.")
    try:
        # Read Configuration variables from config.py file
        print(f"INFO  : Importing Custom Settings from {config_file_path}")
        from config import *
    except ImportError:
        print(f"WARN  : Problem Importing Variables from {config_file_path}")
        warn_on = True
else:
    print(f"WARN  : {config_file_path} File Not Found. Cannot Import Custom Settings.")
    print("        Run Console Command Below to Download File from GitHub Repo")
    print(
        "        wget -O config.py https://raw.github.com/pageauc/pi-timolo2/master/source/config.py"
    )
    print("        or cp config.py.new config.py")
    print("        Will now use default_settings dictionary variable values.")
    warn_on = True

"""
Check if variables were imported from config.py. If not create variable using
the values in the default_settings dictionary above.
"""
for key, val in default_settings.items():
    try:
        exec(key)
    except NameError:
        print("WARN  : config.py Variable Not Found. Setting " + key + " = " + str(val))
        exec(key + "=val")
        warn_on = True

# Setup logging per config.py variables.
if LOG_TO_FILE_ON:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        file_name=log_file_path,
        filemode="w",
    )
elif VERBOSE_ON:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
else:
    logging.basicConfig(
        level=logging.CRITICAL,
        format="%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
logging.info("picamera2 and libcamera logging Disabled.")
logging.warning("Some DEBUG messages may still appear.")
# import specified pantilt library based on config.py setting
if PANTILT_ON:
    pan_x, tilt_y = PANTILT_HOME
    if PANTILT_IS_PIMORONI:
        try:
            import pantilthat
        except ImportError:
            print("ERROR : Import Pimoroni PanTiltHat Python Library per")
            print("        sudo apt install pantilthat")
            print("        Enable I2C support using sudo raspi-config")
            sys.exit()
        try:
            pantilthat.pan(pan_x)
        except IOError:
            print("ERROR: pimoroni pantilthat hardware problem")
            print("       if pimoroni pantilt installed check that I2C enabled in raspi-config.")
            print("if waveshare or conpatible pantilt installed perform the following")
            print("nano edit config.py per below")
            print("    nano config.py")
            print("Change value of variable per below. ctrl-x y to save and exit")
            print("    PANTILT_IS_PIMORONI = False")
            sys.exit()
        pantilt_is = "Pimoroni"
    else:
        try:
            # import pantilthat
            from waveshare.pantilthat import PanTilt
        except ImportError:
            print("ERROR: Install Waveshare PanTiltHat Python Library per")
            print(
                "        curl -L https://raw.githubusercontent.com/pageauc/waveshare.pantilthat/main/install.sh | bash"
            )
            sys.exit()
        try:
            pantilthat = PanTilt()
            pantilthat.pan(pan_x)
        except IOError:
            print("ERROR: pantilthat hardware problem")
            print("nano edit config.py per below")
            print("    nano config.py")
            print("Change value of variable per below. ctrl-x y to save and exit")
            print("    PANTILT_IS_PIMORONI = True")
            sys.exit()
        pantilt_is = "Waveshare"


# Check for user_motion_code.py file to import and error out if not found.
user_motion_filepath = os.path.join(base_dir, "user_motion_code.py")

if not os.path.isfile(user_motion_filepath):
    print(
        "WARN  : %s File Not Found. Cannot Import user_motion_code functions."
        % user_motion_filepath
    )
    warn_on = True
else:
    # Read Configuration variables from config.py file
    try:
        motionCode = True
        import user_motion_code
    except ImportError:
        print("WARN  : Failed Import of File user_motion_code.py Investigate Problem")
        motionCode = False
        warn_on = True

# Give some time to read any warnings
if warn_on and VERBOSE_ON:
    print("")
    print("Please Review Warnings  Wait 10 sec ...")
    time.sleep(10)
    print("Loading Wait ....")

try:
    import cv2
except ImportError:
    if sys.version_info > (2, 9):
        logging.error("Failed to import cv2 opencv for python3")
        logging.error("Try installing opencv for python3")
        logging.error("See https://github.com/pageauc/opencv3-setup")
    else:
        logging.error("Failed to import cv2 for python2")
        logging.error("Try reinstalling per command")
        logging.error("sudo apt-get install python-opencv")
    logging.error(f"Exiting {PROG_NAME} {PROG_VER} Due to Error")
    sys.exit(1)

# import Stream Frame Thread Library
try:
    from strmpilibcam import CamStream
except ImportError:
    logging.error("Problem importing picamera2 module")
    logging.error("Try command below to import module")
    if sys.version_info > (2, 9):
        logging.error("sudo apt install -y python3-picamera2")
    else:
        logging.error("sudo apt install -y python3-picamera2")
    logging.error(f"Exiting {PROG_NAME} {PROG_VER} Due to Error")
    sys.exit(1)


# Check if plugins are on and import as required
if PLUGIN_ON:  # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(base_dir, "plugins")
    # Check if there is a .py at the end of PLUGIN_NAME variable
    if PLUGIN_NAME.endswith(".py"):
        PLUGIN_NAME = PLUGIN_NAME[:-3]  # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, PLUGIN_NAME + ".py")
    logging.info("pluginEnabled - loading PLUGIN_NAME %s", pluginPath)
    if not os.path.isdir(pluginDir):
        logging.error("plugin Directory Not Found at %s", pluginDir)
        logging.error("Rerun github curl install script to install plugins")
        logging.error(
            "https://github.com/pageauc/pi-timolo/wiki/"
            "How-to-Install-or-Upgrade#quick-install"
        )
        logging.error(f"Exiting {PROG_NAME} {PROG_VER} Due to Error")
        sys.exit(1)
    elif not os.path.isfile(pluginPath):
        logging.error("File Not Found PLUGIN_NAME %s", pluginPath)
        logging.error("Check Spelling of PLUGIN_NAME Value in %s", config_file_path)
        logging.error("------- Valid Names -------")
        validPlugin = glob.glob(pluginDir + "/*py")
        validPlugin.sort()
        for entry in validPlugin:
            pluginFile = os.path.basename(entry)
            plugin = pluginFile.rsplit(".", 1)[0]
            if not ((plugin == "__init__") or (plugin == "current")):
                logging.error("        %s", plugin)
        logging.error("------- End of List -------")
        logging.error("Note: PLUGIN_NAME Should Not have .py Ending.")
        logging.error("or Rerun github curl install command.  See github wiki")
        logging.error(
            "https://github.com/pageauc/pi-timolo/wiki/"
            "How-to-Install-or-Upgrade#quick-install"
        )
        logging.error(f"Exiting {PROG_NAME} {PROG_VER} Due to Error")
        sys.exit(1)
    else:
        pluginCurrent = os.path.join(pluginDir, "current.py")
        try:  # Copy image file to recent folder
            logging.info("Copy %s to %s", pluginPath, pluginCurrent)
            shutil.copy(pluginPath, pluginCurrent)
        except OSError as err:
            logging.error(
                "Copy Failed from %s to %s - %s", pluginPath, pluginCurrent, err
            )
            logging.error("Check permissions, disk space, Etc.")
            logging.error(f"Exiting {PROG_NAME} {PROG_VER} Due to Error")
            sys.exit(1)
        logging.info("Import Plugin %s", pluginPath)
        sys.path.insert(0, pluginDir)  # add plugin Directory to program PATH
        from plugins.current import *

        try:
            if os.path.isfile(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.isfile(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
        except OSError as err:
            logging.warning("Failed Removal of %s - %s", pluginCurrentpyc, err)
            time.sleep(5)
else:
    logging.info("No Plugin Enabled per PLUGIN_ON=%s", PLUGIN_ON)

# -------------------  End import of python library modules --------------------

# Turn on VERBOSE_ON when DEBUG_ON mode is enabled
if DEBUG_ON:
    VERBOSE_ON = True

# Make sure image format extention starts with a dot
if not IMAGE_FORMAT.startswith(".", 0, 1):
    IMAGE_FORMAT = "." + IMAGE_FORMAT

# ==================================
#      System Variables
# Should Not need to be customized
# ==================================
SECONDS2MICRO = 1000000  # Used to convert from seconds to microseconds
day_mode = False  # default should always be False.
MOTION_PATH = os.path.join(base_dir, MOTION_DIR)  # Store Motion images
# motion dat file to save currentCount

# Setup filepath's for storing image numbering data
DATA_DIR = "./data"
NUM_PATH_MOTION = os.path.join(DATA_DIR, MOTION_PREFIX + base_file_name + ".dat")
NUM_PATH_TIMELAPSE = os.path.join(DATA_DIR, TIMELAPSE_PREFIX + base_file_name + ".dat")
NUM_PATH_PANO = os.path.join(DATA_DIR, PANO_IMAGE_PREFIX + base_file_name + ".dat")
NUM_PATH_PANTILT_SEQ = os.path.join(
    DATA_DIR, PANTILT_SEQ_IMAGE_PREFIX + base_file_name + ".dat"
)
TIMELAPSE_PATH = os.path.join(base_dir, TIMELAPSE_DIR)  # Store Time Lapse images

# Colors for drawing lines
cvWhite = (255, 255, 255)
cvBlack = (0, 0, 0)
cvBlue = (255, 0, 0)
cvGreen = (0, 255, 0)
cvRed = (0, 0, 255)
LINE_THICKNESS = 1  # Thickness of opencv drawing lines
LINE_COLOR = cvWhite  # color of lines to highlight motion stream area
image_width = IMAGE_WIDTH
image_height = IMAGE_HEIGHT
if DARK_GAIN > 16:
    DARK_GAIN = 16

# ------------------------------------------------------------------------------
def piCamFound():
    try:
        # Use libcamera-hello to check if the camera is detected
        result = subprocess.run(['libcamera-hello', '--list-cameras'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            sensor = None
            for line in result.stdout.splitlines():
                if "Available Pi Cameras:" in line:
                    continue
                if ":" in line:
                    sensor = line.split()[2]  # Extract the sensor name
                    break

            if sensor:
                # Map sensor to camera version
                if sensor == "ov5647":
                    pi_sensor = "ov5647"
                    pi_ver = "V1"
                elif sensor == "imx219":
                    pi_sensor = "imx219"
                    pi_ver = "V2"
                elif sensor == "imx477":
                    pi_sensor = "imx477"
                    pi_ver = "HQ"
                elif sensor == "imx708":
                    pi_sensor = "imx708"
                    pi_ver = "Arducam"
                else:
                    pi_sensor = "Unknown"
                    pi_ver = "Unknown"
                logging.info(f"Sensor: {sensor} Ver: {pi_ver} RPI Camera module")
                return True
            else:
                logging.error("No sensor information Found.")
                return False
        logging.error('Failed to find a Raspberry Pi Camera')
        sys.exit(1)
    except FileNotFoundError:
        logging.error("libcamera-hello not found.\nAre you running this on a Raspberry Pi with libcamera installed?")
        return False


# ------------------------------------------------------------------------------
def getMaxResolution():
    try:
        # Run libcamera-hello to list camera details
        result = subprocess.run(['libcamera-hello', '--list-cameras'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(result.stdout)

            # Parse the output to find the maximum resolution
            max_resolution = None
            for line in result.stdout.splitlines():
                if "[" in line and "x" in line and "]" in line:
                    # Extract the resolution from the camera description line
                    resolution_part = line.split("[")[1].split("]")[0]  # Extract the part inside square brackets
                    if "x" in resolution_part:
                        max_resolution = resolution_part
                        break

            if max_resolution:
                logging.info(f"{max_resolution}")
                cam_resolution = max_resolution.split('x')
                try:
                    for num in cam_resolution:
                        im_W = int(cam_resolution[0])
                        im_H = int(cam_resolution[1])
                    return (im_W, im_H)
                except ValueError:
                    return None
            else:
                logging.warning("No resolution information Found.")
                return None
        else:
            logging.error("Could Not Detect a RPI Camera.")
            print(result.stderr)
    except FileNotFoundError:
        logging.error("libcamera-hello not found.\nAre you running this on a Raspberry Pi with libcamera installed?")
    sys.exit(1)

if piCamFound():
    cam_max_resolution = getMaxResolution()
    if cam_max_resolution is not None:
        imageWidthMax = cam_max_resolution[0]
        imageHeightMax = cam_max_resolution[1]
        # Round image resolution to avoid picamera errors
        if image_width > imageWidthMax:
            image_width = imageWidthMax
        if image_height > imageHeightMax:
            image_height = imageHeightMax
else:
    sys.exit(1)

# increase size of MOTION_TRACK_QUICK_PIC_ON image
bigImage = MOTION_TRACK_QUICK_PIC_BIGGER
bigImageWidth = int(STREAM_WIDTH * bigImage)
bigImageHeight = int(STREAM_HEIGHT * bigImage)

TRACK_TRIG_LEN = MOTION_TRACK_TRIG_LEN  # Pixels moved to trigger motion photo
# Don't track progress until this Len reached.
TRACK_TRIG_LEN_MIN = int(MOTION_TRACK_TRIG_LEN / 6)
# Set max overshoot triglen allowed half cam height
TRACK_TRIG_LEN_MAX = int(STREAM_HEIGHT / 2)
# Timeout seconds Stops motion tracking when no activity
TRACK_TIMEOUT = MOTION_TRACK_TIMEOUT_SEC

# OpenCV Contour sq px area must be greater than this.
MIN_AREA = MOTION_TRACK_MIN_AREA
BLUR_SIZE = 10  # OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20  # OpenCV setting for difference image threshold


# ------------------------------------------------------------------------------
def CheckJpgQuality(im_jpg_quality):
    # Fix range Errors  Use zero to set default quality to 85
    if im_jpg_quality < 1:
        im_jpg_quality = 85
    elif im_jpg_quality > 100:
        im_jpg_quality = 100
    return im_jpg_quality


# ------------------------------------------------------------------------------
def checkConfig():
    """
    Check if both User disabled everything
    in config.py. At least one option needs to be enabled
    """
    if not MOTION_TRACK_ON and not TIMELAPSE_ON and not PANTILT_SEQ_ON and not PANO_ON and not VIDEO_REPEAT_ON:
        error_ext = (
            "You need to have Motion, Timelapse, PanTilt Seq, Pano or Video Repeat turned ON\n"
            "MOTION_TRACK_ON=%s TIMELAPSE_ON=%s PANTILT_SEQ_ON=%s PANO_ON=%s VIDEO_REPEAT_ON=%s"
            % (MOTION_TRACK_ON, TIMELAPSE_ON, PANTILT_SEQ_ON, PANO_ON, VIDEO_REPEAT_ON)
        )
        if VERBOSE_ON:
            logging.error(error_text)
        else:
            sys.stdout.write(error_text)
        sys.exit(1)


# ------------------------------------------------------------------------------
def getLastSubdir(dir_name):
    """Scan for directories and return most recent"""
    dir_list = [
        name
        for name in os.listdir(dir_name)
        if os.path.isdir(os.path.join(dir_name, name))
    ]
    if len(dir_list) > 0:
        last_subdir = sorted(dir_list)[-1]
        last_subdir = os.path.join(dir_name, last_subdir)
    else:
        last_subdir = dir_name
    return last_subdir


# ------------------------------------------------------------------------------
def createSubdir(dir_name, filename_prefix):
    """
    Create a subdirectory in dir_name with
    unique name based on filename_prefix and date time
    """
    right_now = datetime.datetime.now()
    # Specify folder naming
    sub_dir_name = "%s%d-%02d%02d-%02d%02d" % (
        filename_prefix,
        right_now.year,
        right_now.month,
        right_now.day,
        right_now.hour,
        right_now.minute,
    )
    sub_dir_path = os.path.join(dir_name, sub_dir_name)
    if not os.path.isdir(sub_dir_path):
        try:
            os.makedirs(sub_dir_path)
        except OSError as err:
            logging.error(
                "Cannot Create Directory %s - %s, using default location.",
                sub_dir_path,
                err,
            )
            sub_dir_path = dir_name
        else:
            logging.info(f"Created {sub_dir_path}")
    else:
        sub_dir_path = dir_name
    return sub_dir_path


# ------------------------------------------------------------------------------
def subDirCheckMaxFiles(dir_name, files_max):
    """Count number of files in a folder path"""
    file_list = glob.glob(dir_name + "/*jpg")
    count = len(file_list)
    if count > files_max:
        make_new_dir = True
        logging.info(f"Total Files in {dir_name} Exceeds {files_max}")
    else:
        make_new_dir = False
    return make_new_dir


# ------------------------------------------------------------------------------
def subDirCheckMaxHrs(dir_name, hrs_max, filename_prefix):
    """
    Note to self need to add error checking
    extract the date-time from the dir_name name
    """
    dirName = os.path.split(dir_name)[1]  # split dir path and keep dirName
    # remove filename_prefix from dirName so just date-time left
    dirStr = dirName.replace(filename_prefix, "")
    # convert string to datetime
    dirDate = datetime.datetime.strptime(dirStr, "%Y-%m%d-%H%M")
    right_now = datetime.datetime.now()  # get datetime now
    diff = right_now - dirDate  # get time difference between dates
    days, seconds = diff.days, diff.seconds
    dir_age_hours = float(days * 24 + (seconds / 3600.0))  # convert to hours
    if dir_age_hours > hrs_max:  # See if hours are exceeded
        make_new_dir = True
        logging.info(f"MaxHrs {dir_age_hours} Exceeds {hrs_max} for {dir_name}")
    else:
        make_new_dir = False
    return make_new_dir


# ------------------------------------------------------------------------------
def subDirChecks(max_hours, max_files, dir_name, filename_prefix):
    """Check if motion SubDir needs to be created"""
    if max_hours < 1 and max_files < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', dir_name)
        sub_dir_path = dir_name
    else:
        sub_dir_path = getLastSubdir(dir_name)
        if sub_dir_path == dir_name:  # No subDir Found
            logging.info(f"No sub folders Found in {dir_name}")
            sub_dir_path = createSubdir(dir_name, filename_prefix)
        # Check MaxHours Folder Age Only
        elif max_hours > 0 and max_files < 1:
            if subDirCheckMaxHrs(sub_dir_path, max_hours, filename_prefix):
                sub_dir_path = createSubdir(dir_name, filename_prefix)
        elif max_hours < 1 and max_files > 0:  # Check Max Files Only
            if subDirCheckMaxFiles(sub_dir_path, max_files):
                sub_dir_path = createSubdir(dir_name, filename_prefix)
        elif max_hours > 0 and max_files > 0:  # Check both Max Files and Age
            if subDirCheckMaxHrs(sub_dir_path, max_hours, filename_prefix):
                if subDirCheckMaxFiles(sub_dir_path, max_files):
                    sub_dir_path = createSubdir(dir_name, filename_prefix)
                else:
                    logging.info(f"max_files Not Exceeded in {sub_dir_path}")
    os.path.abspath(sub_dir_path)
    return sub_dir_path


# ------------------------------------------------------------------------------
def makeMediaDir(dir_path):
    """Create a folder sequence"""
    make_dir = False
    if not os.path.isdir(dir_path):
        make_dir = True
        logging.info(f"Create Folder {dir_path}")
        try:
            os.makedirs(dir_path)
        except OSError as err_msg:
            logging.error(f"Could Not Create {dir_path}: {err_msg}")
            sys.exit(1)
    return make_dir


# ------------------------------------------------------------------------------
def checkMediaPaths():
    """
    Checks for image folders and
    create them if they do not already exist.
    """
    makeMediaDir(DATA_DIR)

    if MOTION_TRACK_ON:
        if makeMediaDir(MOTION_PATH):
            if os.path.isfile(NUM_PATH_MOTION):
                logging.info("Delete Motion dat File %s", NUM_PATH_MOTION)
                os.remove(NUM_PATH_MOTION)
    if TIMELAPSE_ON:
        if makeMediaDir(TIMELAPSE_PATH):
            if os.path.isfile(NUM_PATH_TIMELAPSE):
                logging.info("Delete TimeLapse dat file %s", NUM_PATH_TIMELAPSE)
                os.remove(NUM_PATH_TIMELAPSE)
    # Check for Recent Image Folders and create if they do not already exist.
    if MOTION_RECENT_MAX > 0:
        makeMediaDir(MOTION_RECENT_DIR)
    if TIMELAPSE_RECENT_MAX > 0:
        makeMediaDir(TIMELAPSE_RECENT_DIR)
    if PANTILT_SEQ_ON:
        makeMediaDir(PANTILT_SEQ_IMAGES_DIR)
        if PANTILT_SEQ_RECENT_MAX > 0:
            makeMediaDir(PANTILT_SEQ_RECENT_DIR)
    if PANO_ON:
        makeMediaDir(PANO_DIR)
        makeMediaDir(PANO_IMAGES_DIR)


# ------------------------------------------------------------------------------
def deleteOldFiles(max_files, dir_path, filename_prefix):
    """
    Delete Oldest files gt or eq to maxfiles that match file_name filename_prefix
    """
    try:
        file_list = sorted(
            glob.glob(os.path.join(dir_path, filename_prefix + "*")), key=os.path.getmtime
        )
    except OSError as err_msg:
        logging.error(f"Problem Reading Directory {dir_path} - {err_msg}")
    else:
        while len(file_list) >= max_files:
            oldest = file_list[0]
            oldestFile = oldest
            try:  # Remove oldest file in recent folder
                file_list.remove(oldest)
                logging.info(f"{oldestFile}")
                os.remove(oldestFile)
            except OSError as err_msg:
                logging.error(f"Failed {oldestFile}: {err_msg}")


# ------------------------------------------------------------------------------

def makeRelSymlink(sourcefile_namePath, symDestDir):
    '''
    Creates a relative symlink in the specified symDestDir
    that points to the Target file via a relative rather than
    absolute path. If a symlink already exists it will be replaced.
    Warning message will be displayed if symlink path is a file
    rather than an existing symlink.
    '''
    # Initialize target and symlink file paths
    targetDirPath = os.path.dirname(sourcefile_namePath)
    srcfile_name = os.path.basename(sourcefile_namePath)
    symDestFilePath = os.path.join(symDestDir, srcfile_name)
    # Check if symlink already exists and unlink if required.
    if os.path.islink(symDestFilePath):
        logging.info("Remove Existing Symlink at %s ", symDestFilePath)
        os.unlink(symDestFilePath)
    # Check if symlink path is a file rather than a symlink. Error out if required
    if os.path.isfile(symDestFilePath):
        logging.warning("Failed. File Exists at %s." % symDestFilePath)
        return

    # Initialize required entries for creating a relative symlink to target file
    absTargetDirPath = os.path.abspath(targetDirPath)
    absSymDirPath = os.path.abspath(symDestDir)
    relativeDirPath = os.path.relpath(absTargetDirPath, absSymDirPath)
    # Initialize relative symlink entries to target file.

    symFilePath = os.path.join(relativeDirPath, srcfile_name)
    # logging.info("ln -s %s %s ", symFilePath, symDestFilePath)
    os.symlink(symFilePath, symDestFilePath)  # Create the symlink
    # Check if symlink was created successfully
    if os.path.islink(symDestFilePath):
        logging.info(f"Saved at {symDestFilePath}")
    else:
        logging.warning(f"Failed to Create Symlink at {symDestFilePath}")


# ------------------------------------------------------------------------------
def saveRecent(recent_max, recent_dir, file_path, filename_prefix):
    """
    Create a symlink file in recent folder (timelapse or motion subfolder)
    Delete Oldest symlink file if recent_max exceeded.
    """
    show_log = False
    if recent_max > 0:
        deleteOldFiles(recent_max, os.path.abspath(recent_dir), filename_prefix)
        makeRelSymlink(file_path, recent_dir)


# ------------------------------------------------------------------------------
def filesToDelete(mediaDirPath, extension=IMAGE_FORMAT):
    """
    Deletes files of specified format extension
    by walking folder structure from specified mediaDirPath
    """
    return sorted(
        (
            os.path.join(dirname, file_name)
            for dirname, dirnames, file_names in os.walk(mediaDirPath)
            for file_name in file_names
            if file_name.endswith(extension)
        ),
        key=lambda fn: os.stat(fn).st_mtime,
        reverse=True,
    )


# ------------------------------------------------------------------------------
def freeSpaceUpTo(freeMB, mediaDir, extension=IMAGE_FORMAT):
    """
    Walks mediaDir and deletes oldest files until SPACE_TARGET_MB is achieved.
    You should Use with Caution this feature.
    """
    mediaDirPath = os.path.abspath(mediaDir)
    if os.path.isdir(mediaDirPath):
        MB2Bytes = 1048576  # Conversion from MB to Bytes
        targetFreeBytes = freeMB * MB2Bytes
        file_list = filesToDelete(mediaDir, extension)
        totFiles = len(file_list)
        delcnt = 0
        logging.info("Session Started")
        while file_list:
            statv = os.statvfs(mediaDirPath)
            availFreeBytes = statv.f_bfree * statv.f_bsize
            if availFreeBytes >= targetFreeBytes:
                break
            filePath = file_list.pop()
            try:
                os.remove(filePath)
            except OSError as err:
                logging.error("Del Failed %s", filePath)
                logging.error("Error is %s", err)
            else:
                delcnt += 1
                logging.info("Del %s", filePath)
                logging.info(
                    "Target=%i MB  Avail=%i MB  Deleted %i of %i Files ",
                    targetFreeBytes / MB2Bytes,
                    availFreeBytes / MB2Bytes,
                    delcnt,
                    totFiles,
                )
                # Avoid deleting more than 1/4 of files at one time
                if delcnt > totFiles / 4:
                    logging.warning("Max Deletions Reached %i of %i", delcnt, totFiles)
                    logging.warning(
                        "Deletions Restricted to 1/4 of " "total files per session."
                    )
                    break
        logging.info("Session Ended")
    else:
        logging.error("Directory Not Found - %s", mediaDirPath)


# ------------------------------------------------------------------------------
def freeDiskSpaceCheck(lastSpaceCheck):
    """
    Perform Disk space checking and Clean up
    if enabled and return datetime done
    to reset ready for next sched date/time
    """
    if SPACE_TIMER_HOURS > 0:  # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if (
            datetime.datetime.now() - lastSpaceCheck
        ).total_seconds() > SPACE_TIMER_HOURS * 3600:
            lastSpaceCheck = datetime.datetime.now()
            if SPACE_TARGET_MB < 100:  # set freeSpaceMB to reasonable value if too low
                diskFreeMB = 100
            else:
                diskFreeMB = SPACE_TARGET_MB
            logging.info(
                "SPACE_TIMER_HOURS=%i  diskFreeMB=%i  SPACE_MEDIA_DIR=%s SPACE_TARGET_EXT=%s",
                SPACE_TIMER_HOURS,
                diskFreeMB,
                SPACE_MEDIA_DIR,
                SPACE_TARGET_EXT,
            )
            freeSpaceUpTo(diskFreeMB, SPACE_MEDIA_DIR, SPACE_TARGET_EXT)
    return lastSpaceCheck


# ------------------------------------------------------------------------------
def getCurrentCount(numberpath, numberstart):
    """
    Create a .dat file to store currentCount
    or read file if it already Exists
    """
    if not os.path.isfile(numberpath):
        # Create numberPath file if it does not exist
        logging.info("Creating New File %s numberstart= %s", numberpath, numberstart)
        open(numberpath, "w").close()
        f = open(numberpath, "w+")
        f.write(str(numberstart))
        f.close()
    # Read the numberPath file to get the last sequence number
    with open(numberpath, "r") as f:
        writeCount = f.read()
        f.closed
        try:
            numbercounter = int(writeCount)
        # Found Corrupt dat file since cannot convert to integer
        except ValueError:
            # Try to determine if this is motion or timelapse
            if numberpath.find(MOTION_PREFIX) > 0:
                filePath = MOTION_PATH + "/*" + IMAGE_FORMAT
                fprefix = MOTION_PATH + MOTION_PREFIX + IMAGE_NAME_PREFIX
            else:
                filePath = TIMELAPSE_PATH + "/*" + IMAGE_FORMAT
                fprefix = TIMELAPSE_PATH + TIMELAPSE_PREFIX + IMAGE_NAME_PREFIX
            try:
                # Scan image folder for most recent file
                # and try to extract most recent number counter
                newest = max(glob.iglob(filePath), key=os.path.getctime)
                writeCount = newest[len(fprefix) + 1 : newest.find(IMAGE_FORMAT)]
            except:
                writeCount = numberstart
            try:
                numbercounter = int(writeCount) + 1
            except ValueError:
                numbercounter = numberstart
            logging.warning(
                "Found Invalid Data in %s Resetting Counter to %s",
                numberpath,
                numbercounter,
            )
        f = open(numberpath, "w+")
        f.write(str(numbercounter))
        f.close()
        f = open(numberpath, "r")
        writeCount = f.read()
        f.close()
        numbercounter = int(writeCount)
    return numbercounter


# ------------------------------------------------------------------------------
def writeTextToImage(image_name, date_to_print, currentday_mode):
    """
    Function to write date/time stamp
    directly on top or bottom of images.
    """
    if SHOW_TEXT_WHITE:
        text_foreground_colour = (255, 255, 255)  # rgb settings for white text text_foreground_colour
        text_colour = "White"
    else:
        text_foreground_colour = (0, 0, 0)  # rgb settings for black text text_foreground_colour
        text_colour = "Black"
        if SHOW_TEXT_WHITE_NIGHT and (not currentday_mode):
            # rgb settings for black text text_foreground_colour
            text_foreground_colour = (255, 255, 255)
            text_colour = "White"
    im_data = cv2.imread(image_name)
    # This is grayscale image so channels is not avail or used
    height, width, channels = im_data.shape
    # centre text and compensate for graphics text being wider
    im_x = int((width / 2) - (len(image_name) * 2))
    if SHOW_TEXT_BOTTOM:
        im_y = height - 50  # show text at bottom of image
    else:
        im_y = 10  # show text at top of image
        
    TEXT = IMAGE_NAME_PREFIX + date_to_print
    font_path = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    font = ImageFont.truetype(font_path, SHOW_TEXT_FONT_SIZE, encoding="unic")
    try:
        image_text = TEXT.decode("utf-8")  # required for python2
    except:
        image_text = TEXT  # Just set for python3
        
    im_draw = Image.open(image_name)

    try:  # Read exif data since ImageDraw does not save this metadata
        metadata = pyexiv2.ImageMetadata(image_name)
        metadata.read()
    except:
        pass
    draw = ImageDraw.Draw(im_draw)
    draw.text((im_x, im_y), image_text, text_foreground_colour, font=font)
    if IMAGE_FORMAT.lower == ".jpg" or IMAGE_FORMAT.lower == ".jpeg":
        im_draw.save(image_name, quality="keep")
    else:
        im_draw.save(image_name)
    logging.info(f"Added {text_colour} Image Text [ {image_text} ]")
    try:
        metadata.write()  # Write previously saved exif data to image file
    except:
        logging.warning("Image EXIF Data Not Transferred.")
    logging.info(f"Saved {image_name}")


# ------------------------------------------------------------------------------
def writeCounter(counter, counter_path):
    """
    Write next counter number
    to specified counter_path dat file
    to remember where counter is to start next in case
    app shuts down.
    """
    str_count = str(counter)
    if not os.path.isfile(counter_path):
        logging.info("Create New Counter File Counter=%s %s", str_count, counter_path)
        open(counter_path, "w").close()
    f = open(counter_path, "w+")
    f.write(str_count)
    f.close()
    logging.info("Next Counter=%s %s", str_count, counter_path)


# ------------------------------------------------------------------------------
def postImageProcessing(
    numberon,
    counterstart,
    countermax,
    counter,
    recycle,
    counterpath,
    file_name,
    currentday_mode,
    ):
    """
    If required process text to display directly on image
    """
    right_now = datetime.datetime.now()
    if SHOW_DATE_ON_IMAGE:
        dateTimeText = "%04d%02d%02d_%02d:%02d:%02d" % (
            right_now.year,
            right_now.month,
            right_now.day,
            right_now.hour,
            right_now.minute,
            right_now.second,
        )
        if numberon:
            if not recycle and countermax > 0:
                counterStr = "%i/%i " % (counter, counterstart + countermax)
                imageText = counterStr + dateTimeText
            else:
                counterStr = "%i  " % (counter)
                imageText = counterStr + dateTimeText
        else:
            imageText = dateTimeText
        # Now put the imageText on the current image
        #try:  # This will fail for a video file so pass
        writeTextToImage(file_name, imageText, currentday_mode)
        #except:
        #    pass
    # Process currentCount for next image if number sequence is enabled
    if numberon:
        counter += 1
        if countermax > 0:
            if counter >= counterstart + countermax:
                if recycle:
                    counter = counterstart
                else:
                    counter = counterstart + countermax + 1
                    logging.warning(
                        "Exceeded Image Count numberMax=%i for %s \n",
                        countermax,
                        file_name,
                    )
        # write next image counter number to dat file
        writeCounter(counter, counterpath)
    return counter


# ------------------------------------------------------------------------------
def getVideoName(path, filename_prefix, numberon, counter):
    """build image file names by number sequence or date/time"""
    if numberon:
        if MOTION_VIDEO_ON or VIDEO_REPEAT_ON:
            file_name = os.path.join(path, filename_prefix + str(counter) + ".h264")
    else:
        if MOTION_VIDEO_ON or VIDEO_REPEAT_ON:
            right_now = datetime.datetime.now()
            file_name = "%s/%s%04d%02d%02d-%02d%02d%02d.h264" % (
                path,
                filename_prefix,
                right_now.year,
                right_now.month,
                right_now.day,
                right_now.hour,
                right_now.minute,
                right_now.second,
            )
    return file_name


# ------------------------------------------------------------------------------
def getImagefile_name(path, filename_prefix, numberon, counter):
    """build image file names by number sequence or date/time"""
    if numberon:
        file_name = os.path.join(path, filename_prefix + str(counter) + IMAGE_FORMAT)
    else:
        right_now = datetime.datetime.now()
        file_name = "%s/%s%04d%02d%02d-%02d%02d%02d%s" % (
            path,
            filename_prefix,
            right_now.year,
            right_now.month,
            right_now.day,
            right_now.hour,
            right_now.minute,
            right_now.second,
            IMAGE_FORMAT,
        )
    return file_name


# ------------------------------------------------------------------------------
def showBox(file_name):
    """
    Show stream image detection area on image to align camera
    This is a quick fix for restricting motion detection
    to a portion of the final image. Change the stream image size
    on line 206 and 207 above
    Adjust track config.py file MOTION_TRACK_TRIG_LEN as required.
    """
    working_image = cv2.imread(file_name)
    x1y1 = (
        int((IMAGE_WIDTH - STREAM_WIDTH) / 2),
        int((image_height - STREAM_HEIGHT) / 2),
    )
    x2y2 = (x1y1[0] + STREAM_WIDTH, x1y1[1] + STREAM_HEIGHT)
    cv2.rectangle(working_image, x1y1, x2y2, LINE_COLOR, LINE_THICKNESS)
    cv2.imwrite(file_name, working_image)


# ------------------------------------------------------------------------------
def takeMotionQuickImage(image, file_name):
    """Enlarge and Save stream image if MOTION_TRACK_QUICK_PIC_ON=True"""
    big_image = (
        cv2.resize(image, (bigImageWidth, bigImageHeight)) if bigImage != 1 else image
    )
    cv2.imwrite(file_name, big_image)
    logging.info("Saved %ix%i Image to %s", bigImageWidth, bigImageHeight, file_name)


# ------------------------------------------------------------------------------
def saveGrayscaleImage(file_name):
    """
    Use PIL to read and resave image as greyscale per IMAGE_GRAYSCALE variable
    in config.py setting
    """
    image = Image.open(file_name)
    bw_image = image.convert("L")
    bw_image.save(file_name)


# ------------------------------------------------------------------------------
def saveRotatateImage(file_name, deg):
    """
    Use PIL to read, rotate and resave rotated image if IMA
    """
    valid_deg = [0, 90, 180, 270, -90, -180, -270]
    if deg is None:
        return
    elif deg in valid_deg:
        image = Image.open(file_name)
        rot_image = image.rotate(deg)
        rot_image.save(file_name)
    else:
        logging.warning(f"Rotation {deg} not valid.")
        logging.warning("Valid entries are None, 0, 90, 180, 270, -90, -180, -270")


# ------------------------------------------------------------------------------
def getExposureSettings(px_ave):
    """
    Use the px_ave and DARK_START_PXAVE threshold to set
    analogue_gain for day or darkness
    """
    if px_ave > DARK_START_PXAVE:
        exposure_microsec = 0    # Auto
        analogue_gain = 0        # Auto
    else:
        exposure_sec = DARK_MAX_EXP_SEC / DARK_START_PXAVE
        exposure_microsec = int(exposure_sec * (DARK_START_PXAVE - px_ave) * SECONDS2MICRO)
        analogue_gain = DARK_GAIN
    return exposure_microsec, analogue_gain


# ------------------------------------------------------------------------------
def takeImage(file_path, im_data):
    """
    Get camera settings, configure camera for dark or bright conditions based on px_ave
    Take and save still image
    """
    px_ave = getStreamPixAve(im_data)
    exposure_microsec, analogue_gain = getExposureSettings(px_ave)
    retries = 0
    total_retries = 3
    while retries < total_retries:
        try:
            picam2 = Picamera2()  # Initialize the camera
            config = picam2.create_preview_configuration({"size": (image_width, image_height)},
                                                          transform=Transform(vflip=IMAGE_VFLIP,
                                                                              hflip=IMAGE_HFLIP))
            picam2.configure(config)
        except RuntimeError:
            retries += 1
            logging.warning('Camera Error. Could Not Configure')
            logging.warning(f'Retry {retries} of {total_retries}')
            picam2.close()  # Close the camera instance
            if retries > total_retries:
                logging.error('Retries Exceeded. Exiting Due to Camera Problem. ')
                sys.exit(1)
            else:
                time.sleep(4)
                continue
        break
    picam2.set_controls({"ExposureTime": exposure_microsec,
                         "AnalogueGain": analogue_gain,
                         "FrameDurationLimits": (exposure_microsec, exposure_microsec)})
    picam2.start()  # Start the camera instance

    # Allow some time for the camera to adjust to the light conditions
    if analogue_gain < 1:  # set for daylight. Auto is 0
        time.sleep(4) # Allow time for camera to warm up
    else:
        logging.info(f'Low Light {px_ave}/{DARK_START_PXAVE} px_ave')
        time.sleep(analogue_gain) # Allow time for camera to adjust for long exposure

    logging.info(f"ImageSize=({image_width}x{image_height}) vflip={IMAGE_VFLIP} hflip={IMAGE_HFLIP}")
    logging.info(f"px_ave={px_ave}, Exposure={exposure_microsec} microsec, Gain={analogue_gain} Auto is 0")
    logging.info(f"Save Image to {file_path}")
    picam2.capture_file(file_path)      # Capture the image
    picam2.close()  # Close the camera instance
    if IMAGE_GRAYSCALE:
        saveGrayscaleImage(file_path)
    if IMAGE_ROTATION is not None:
        saveRotatateImage(file_path, IMAGE_ROTATION)
    if IMAGE_SHOW_STREAM:  # Show motion area on full image to align camera
        showBox(file_path)


# ------------------------------------------------------------------------------
def getMotionTrackPoint(grayimage_1, grayimage_2):
    """
    Process two cropped grayscale images.
    check for motion and return center point
    of motion for largest contour.
    """
    movementCenterPoint = []  # initialize list of movementCenterPoints
    biggestArea = MIN_AREA
    # Get differences between the two greyed images
    differenceimage = cv2.absdiff(grayimage_1, grayimage_2)
    # Blur difference image to enhance motion vectors
    differenceimage = cv2.blur(differenceimage, (BLUR_SIZE, BLUR_SIZE))
    # Get threshold of blurred difference image
    # based on THRESHOLD_SENSITIVITY variable
    retval, thresholdimage = cv2.threshold(
        differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY
    )
    try:
        # opencv2 syntax default
        contours, hierarchy = cv2.findContours(
            thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    except ValueError:
        # opencv 3 syntax
        thresholdimage, contours, hierarchy = cv2.findContours(
            thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    if contours:
        for c in contours:
            cArea = cv2.contourArea(c)
            if cArea > biggestArea:
                biggestArea = cArea
                (x, y, w, h) = cv2.boundingRect(c)
                cx = int(x + w / 2)  # x center point of contour
                cy = int(y + h / 2)  # y center point of contour
                movementCenterPoint = [cx, cy]
    return movementCenterPoint


# ------------------------------------------------------------------------------
def trackMotionDistance(mPoint1, mPoint2):
    """
    Return the triangulated distance between two tracking locations
    """
    x1, y1 = mPoint1
    x2, y2 = mPoint2
    trackLen = abs(math.hypot(x2 - x1, y2 - y1))
    return trackLen


# ------------------------------------------------------------------------------
def getStreamPixAve(streamData):
    """
    Calculate the average pixel values for the specified stream
    used for determining day/night or twilight conditions
    """
    pixAverage = int(np.average(streamData[..., 1]))  # Use 0=red 1=green 2=blue
    return pixAverage


# ------------------------------------------------------------------------------
def checkIfDayStream(currentday_mode, image):
    """Try to determine if it is day, night or twilight."""
    dayPixAverage = 0
    currentday_mode = False
    dayPixAverage = getStreamPixAve(image)
    if dayPixAverage > DARK_START_PXAVE:
        currentday_mode = True
    return currentday_mode


# ------------------------------------------------------------------------------
def timeToSleep(currentday_mode):
    """
    Based on weather it is day or night (exclude twilight)
    return sleepMode boolean based on variable
    settings for IMAGE_NO_NIGHT_SHOTS or IMAGE_NO_DAY_SHOTS config.py variables
    Note if both are enabled then no shots will be taken.
    """
    if IMAGE_NO_NIGHT_SHOTS:
        if currentday_mode:
            sleepMode = False
        else:
            sleepMode = True
    elif IMAGE_NO_DAY_SHOTS:
        sleepMode = False
        if currentday_mode:
            sleepMode = True
    else:
        sleepMode = False
    return sleepMode


# ------------------------------------------------------------------------------
def getSchedStart(date_to_check):
    """
    This function will try to extract a valid date/time from a
    date time formatted string variable
    If date/time is past then try to extract time
    and schedule for current date at extracted time
    """
    good_datetime = datetime.datetime.now()
    if len(date_to_check) > 1:  # Check if TIMELAPSE_START_AT is set
        try:
            # parse and convert string to date/time or return error
            good_datetime = parse(date_to_check)
        except:
            # Is there a colon indicating possible time format exists
            if ":" in date_to_check:
                time_try = date_to_check[date_to_check.find(":") - 2 :]
                # Try to extract time only from string
                try:
                    # See if a valid time is found returns with current day
                    good_datetime = parse(time_try)
                except:
                    logging.error("Bad Date and/or Time Format %s", date_to_check)
                    logging.error(
                        "Use a Valid Date and/or Time "
                        'Format Eg "DD-MMM-YYYY HH:MM:SS"'
                    )
                    good_datetime = datetime.datetime.now()
                    logging.warning(f"Resetting date/time to Now: {good_datetime}")
        # Check if date/time is past
        if good_datetime < datetime.datetime.now():
            if ":" in date_to_check:  # Check if there is a time component
                # Extract possible time component
                time_try = date_to_check[date_to_check.find(":") - 2 :]
                try:
                    # parse for valid time
                    # returns current day with parsed time
                    good_datetime = parse(time_try)
                except:
                    pass  # Do Nothing
    return good_datetime


# ------------------------------------------------------------------------------
def checkSchedStart(schedDate):
    """
    Based on schedule date setting see if current
    datetime is past and return boolean
    to indicate processing can start for
    timelapse or motiontracking
    """
    startStatus = False
    if schedDate < datetime.datetime.now():
        startStatus = True  # sched date/time has passed so start sequence
    return startStatus


# ------------------------------------------------------------------------------
def checkTimer(timer_start, timer_sec):
    """
    Check if timelapse timer has expired
    Return updated start time status of expired timer True or False
    """
    timer_expired = False
    right_now = datetime.datetime.now()
    timeDiff = (right_now - timer_start).total_seconds()
    if timeDiff >= timer_sec:
        timer_expired = True
        timer_start = right_now
    return timer_start, timer_expired


# ------------------------------------------------------------------------------
def takeMiniTimelapse(mo_path, filename_prefix, num_on, motion_num_count, currentday_mode, im_data):
    """
    Take a motion tracking activated mini timelapse sequence
    using yield if motion triggered
    """
    logging.info(
        "START - Run for %i secs with image every %i secs",
        MOTION_TRACK_MINI_TL_SEQ_SEC,
        MOTION_TRACK_MINI_TL_TIMER_SEC,
    )
    check_timelapse_timer = datetime.datetime.now()
    keep_taking_images = True
    image_count = 1
    motion_num_count = getCurrentCount(NUM_PATH_MOTION, MOTION_NUM_START)
    file_name = getImagefile_name(mo_path, filename_prefix, num_on, motion_num_count)
    while keep_taking_images:
        logging.info(f"{image_count}")
        takeImage(file_name, im_data)
        motion_num_count += 1
        writeCounter(motion_num_count, NUM_PATH_MOTION)
        file_name = getImagefile_name(mo_path, filename_prefix, num_on, motion_num_count)
        right_now = datetime.datetime.now()
        timelapse_diff = (right_now - check_timelapse_timer).total_seconds()
        if timelapse_diff > MOTION_TRACK_MINI_TL_SEQ_SEC + 1:
            keep_taking_images = False
        else:
            image_count += 1
            saveRecent(MOTION_RECENT_MAX, MOTION_RECENT_DIR, file_name, filename_prefix)
            time.sleep(MOTION_TRACK_MINI_TL_TIMER_SEC)
    logging.info(f"END - Total {image_count} Images in {timelapse_diff} sec\n")



# ------------------------------------------------------------------------------
def takeVideo(file_name, vid_seconds, vid_W=1280, vid_H=720, vid_fps=25):
    """Take a short motion video if required"""
    logging.info("Start: Size %ix%i for %i sec at %i fps", vid_W, vid_H, vid_seconds, vid_fps)
    if MOTION_VIDEO_ON or VIDEO_REPEAT_ON:
        file_path_mp4 = os.path.join(os.path.dirname(file_name),
                                   os.path.splitext(os.path.basename(file_name))[0] + ".mp4")
        picam2 = Picamera2()
        picam2.configure(picam2.create_video_configuration({"size": (vid_W, vid_H)},
                                                           transform=Transform(vflip=IMAGE_VFLIP,
                                                                               hflip=IMAGE_HFLIP)))
        picam2.set_controls({"FrameRate": vid_fps})
        encoder = H264Encoder(10000000)
        output = FfmpegOutput(file_path_mp4)

        vid_total_retries = 4
        vid_retries = vid_total_retries
        while vid_retries > 0:
            vid_retries -=1
            try:
                picam2.start_recording(encoder, output)
            except RuntimeError:
                logging.warning(f"Camera Error. Retry {vid_retries+1} of {vid_total_retries} Wait ...")
                time.sleep(5)
                continue
            break                
            
        time.sleep(vid_seconds)
        picam2.stop_recording()
        picam2.close()
        if MOTION_RECENT_MAX:
            logging.info(f"Saved Motion Tracking Video to {file_path_mp4}")
        else:
            logging.info(f"Saved Video Repeat to {file_path_mp4}")
        saveRecent(MOTION_RECENT_MAX, MOTION_RECENT_DIR, file_path_mp4, MOTION_PREFIX)
    else:
        logging.warning("You Must have MOTION_VIDEO_ON= True or VIDEO_REPEAT_ON= True")


# ------------------------------------------------------------------------------
def pantiltGoHome():
    """
    Move pantilt to home position. If pantilt installed then this
    can position pantilt to a home position for consistent
    motion tracking and timelapse camera pointing.
    """
    if PANTILT_ON:
        pantilthat.pan(PANTILT_HOME[0])
        time.sleep(PANTILT_SLEEP_SEC)
        pantilthat.tilt(PANTILT_HOME[1])
        time.sleep(PANTILT_SLEEP_SEC)


# ------------------------------------------------------------------------------
def addFilepathSeq(file_path, seq_num):
    """
    Add a sequence number to the file_name just prior to the image format extension.
    """
    index = file_path.find(IMAGE_FORMAT)
    seq_filepath = file_path[:index] + "-" + str(seq_num) + file_path[index:]
    return seq_filepath


# ------------------------------------------------------------------------------
def takePantiltSequence(file_name, day_mode, num_count, num_path, im_data):
    """
    Take a sequence of images based on a list of pantilt positions and save with
    a sequence number appended to the file_name
    """

    if (not day_mode) and PANTILT_SEQ_DAYONLY_ON:
        logging.info('Skip since PANTILT_SEQ_DAYONLY_ON = %s and day_mode = %s',
                     PANTILT_SEQ_DAYONLY_ON, day_mode)
        return
    elif not PANTILT_ON:
        logging.error(f'takePantiltSequence Requires PANTILT_ON=True. Edit in Config.py')
        return

    if MOTION_TRACK_ON and MOTION_TRACK_PANTILT_SEQ_ON:
        seq_prefix = MOTION_PREFIX + IMAGE_NAME_PREFIX
        if PANTILT_SEQ_ON:
            logging.warning('MOTION_TRACK_PANTILT_SEQ_ON takes precedence over PANTILT_SEQ_ON')
            logging.warning('Disable config.py MOTION_TRACK_PANTILT_SEQ_ON setting')
            logging.warning('to Enable Timelapse PANTILT_SEQ_ON option.')
        logging.info("Start Motion Tracking PanTilt Sequence.")
    elif PANTILT_SEQ_ON:
        seq_prefix = PANTILT_SEQ_IMAGE_PREFIX + IMAGE_NAME_PREFIX
        logging.info(f"MOTION_TRACK_ON={MOTION_TRACK_ON}, TIMELAPSE_ON={TIMELAPSE_ON}")
        logging.info(f"PANTILT_SEQ_ON={PANTILT_SEQ_ON} Take Sequence Every {PANTILT_SEQ_TIMER_SEC} sec")
        logging.info(f"Start PanTilt Images at Stops {PANTILT_SEQ_STOPS}")
    # initialize counter to ensure each image file_name is unique
    pantilt_seq_image_num = 0

    for cam_pos in PANTILT_SEQ_STOPS:  # take images at each specified stop
        pantilt_seq_image_num += 1  # Set image numbering for this image
        seq_filepath = addFilepathSeq(file_name, pantilt_seq_image_num)
        pan_x, tilt_y = cam_pos  # set pan tilt values for this image
        pantilthat.pan(pan_x)
        pantilthat.tilt(tilt_y)
        logging.info("pan_x=%i tilt_y=%i", pan_x, tilt_y)
        time.sleep(PANTILT_SLEEP_SEC)
        takeImage(seq_filepath, im_data)
        if MOTION_TRACK_PANTILT_SEQ_ON:
            postImageProcessing(
                MOTION_NUM_ON,
                MOTION_NUM_START,
                MOTION_NUM_MAX,
                num_count,
                MOTION_NUM_RECYCLE_ON,
                NUM_PATH_MOTION,
                seq_filepath,
                day_mode,
            )
            saveRecent(
                MOTION_NUM_MAX,
                MOTION_RECENT_DIR,
                seq_filepath,
                seq_prefix
            )

        elif PANTILT_SEQ_ON:
            postImageProcessing(
                PANTILT_SEQ_NUM_ON,
                PANTILT_SEQ_NUM_START,
                PANTILT_SEQ_NUM_MAX,
                num_count,
                PANTILT_SEQ_NUM_RECYCLE_ON,
                NUM_PATH_PANTILT_SEQ,
                seq_filepath,
                day_mode,
            )
            saveRecent(
                PANTILT_SEQ_NUM_MAX,
                PANTILT_SEQ_RECENT_DIR,
                seq_filepath,
                PANTILT_SEQ_IMAGE_PREFIX,
            )

    if PANTILT_SEQ_NUM_ON:
        num_count += 1
        writeCounter(num_count, NUM_PATH_PANTILT_SEQ)

    deleteOldFiles(PANTILT_SEQ_RECENT_MAX,
                   os.path.abspath(PANTILT_SEQ_RECENT_DIR),
                   PANTILT_SEQ_IMAGE_PREFIX
    )
    pantiltGoHome()  # Center pantilt
    logging.info("... End")
    return num_count


# ------------------------------------------------------------------------------
def takePano(pano_seq_num, day_mode, im_data):
    """
    Take a series of overlapping images using pantilt at specified PANO_CAM_STOPS
    then attempt to stitch the images into one panoramic image. Note this
    will take time so depending on number of cpu cores and speed. The PANO_TIMER
    should be set to avoid multiple stitching operations at once.
    use htop or top to check stitching PID activity.

    Successfuly Stitching needs good lighting so it should be restricted to
    day light hours or sufficient indoor lighting.
    Review pano source image overlap using webserver. Adjust pano stops accordingly.
    """

    if (not day_mode) and PANO_DAYONLY_ON:
        logging.info('Skip since PANO_DAYONLY_ON = %s and day_mode = %s',
                     PANO_DAYONLY_ON, day_mode)
        return

    print("")
    logging.info("Start timer=%i sec  pano_seq_num=%s", PANO_TIMER_SEC, pano_seq_num)

    pano_image_num = 0  # initialize counter to ensure each image file_name is unique
    pano_image_files = (
        ""  # string of contatenated image input pano file_names for stitch command line
    )
    pano_file_path = os.path.join(
        PANO_DIR,
        PANO_IMAGE_PREFIX + IMAGE_NAME_PREFIX + str(pano_seq_num) + IMAGE_FORMAT,
    )

    for cam_pos in PANO_CAM_STOPS:  # take images at each specified stop
        pano_image_num += 1  # Set image numbering for this image
        pan_x, tilt_y = cam_pos  # set pan tilt values for this image
        pano_file_name = os.path.join(
            PANO_IMAGES_DIR,
            PANO_IMAGE_PREFIX
            + IMAGE_NAME_PREFIX
            + str(pano_seq_num)
            + "-"
            + str(pano_image_num)
            + IMAGE_FORMAT,
        )
        pano_image_files += " " + pano_file_name
        pantilthat.pan(pan_x)
        pantilthat.tilt(tilt_y)
        if pano_seq_num == 1:
            time.sleep(0.3)
        time.sleep(PANTILT_SLEEP_SEC)
        takeImage(pano_file_name, im_data)
        logging.info(
            "Size %ix%i Saved %s at cam_pos(%i, %i)",
            image_width,
            image_height,
            pano_file_name,
            pan_x,
            tilt_y,
        )
    # Center pantilt
    pantiltGoHome()
    logging.info("End")

    if not os.path.isfile(PANO_PROG_PATH):
        logging.error("Cannot Find Pano Executable File at %s", PANO_PROG_PATH)
        logging.info("Please run menubox.sh UPGRADE to correct problem")
        logging.warning("Exiting - Cannot Run Image Stitching of Images.")
        return
    if not os.path.isfile("./config.cfg"):
        logging.error("Cannot Find ./config.cfg required for %s", PANO_PROG_PATH)
        logging.info("Please run menubox.sh UPGRADE to correct problem")
        logging.warning("Exiting - Cannot Run Image Stitching of Images.")
        return
    # Create the stitch command line string
    stitch_cmd = PANO_PROG_PATH + " " + pano_file_path + pano_image_files
    try:
        logging.info("Run Image Stitching Command per Below")
        print("%s" % stitch_cmd)
        # spawn stitch command with parameters as seperate task
        proc = subprocess.Popen(
            stitch_cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True
        )
    except IOError:
        logging.error("Failed subprocess %s", stitch_cmd)
    pano_seq_num += 1
    if PANO_NUM_RECYCLE and PANO_NUM_MAX > 0:
        if pano_seq_num >= PANO_NUM_START + PANO_NUM_MAX:
            logging.info(
                "PANO_NUM_RECYCLE Activated. Reset pano_seq_num to %i", PANO_NUM_START
            )
            pano_seq_num = PANO_NUM_START
    writeCounter(pano_seq_num, NUM_PATH_PANO)
    return pano_seq_num


# ------------------------------------------------------------------------------
def videoRepeat():
    """
    This is a special dash cam video mode
    that overrides both timelapse and motion tracking settings
    It has it's own set of settings to manage start, video duration,
    number recycle mode, Etc.
    """
    # Check if folder exist and create if required
    if not os.path.isdir(VIDEO_DIR):
        logging.info("Create videoRepeat Folder %s", VIDEO_DIR)
        os.makedirs(VIDEO_DIR)
    print("--------------------------------------------------------------------")
    print("VideoRepeat . VIDEO_REPEAT_ON=%s" % VIDEO_REPEAT_ON)
    print(
        "   Info ..... Size=%ix%i  VIDEO_PREFIX=%s  VIDEO_FILE_SEC=%i seconds  VIDEO_FPS=%i"
        % (
            VIDEO_REPEAT_WIDTH,
            VIDEO_REPEAT_HEIGHT,
            VIDEO_PREFIX,
            VIDEO_FILE_SEC,
            VIDEO_FPS,
        )
    )
    print("   Vid Path . VIDEO_DIR= %s" % VIDEO_DIR)
    print(
        "   Sched .... VIDEO_START_AT=%s blank=Off or Set Valid Date and/or Time to Start Sequence"
        % VIDEO_START_AT
    )
    print(
        "   Timer .... VIDEO_SESSION_MIN=%i minutes  0=Continuous" % VIDEO_SESSION_MIN
    )
    print(
        "   Num Seq .. VIDEO_NUM_ON=%s  VIDEO_NUM_RECYCLE_ON=%s  VIDEO_NUM_START=%i"
        "  VIDEO_NUM_MAX=%i 0=Continuous"
        % (VIDEO_NUM_ON, VIDEO_NUM_RECYCLE_ON, VIDEO_NUM_START, VIDEO_NUM_MAX)
    )
    print("--------------------------------------------------------------------")
    print(
        "WARNING: VIDEO_REPEAT_ON=%s Suppresses TimeLapse and Motion Settings."
        % VIDEO_REPEAT_ON
    )
    startVideoRepeat = getSchedStart(VIDEO_START_AT)
    if not checkSchedStart(startVideoRepeat):
        logging.info('VIDEO_START_AT = "%s" ', VIDEO_START_AT)
        logging.info(
            "Video Repeat: Sched Start Set For %s  Please Wait ...", startVideoRepeat
        )
        while not checkSchedStart(startVideoRepeat):
            pass
    videoStartTime = datetime.datetime.now()
    lastSpaceCheck = datetime.datetime.now()
    videoCount = 0
    videoNumCounter = VIDEO_NUM_START
    keepRecording = True
    while keepRecording:
        # if required check free disk space and delete older files
        # Set variable SPACE_TARGET_EXT='mp4' and
        # SPACE_MEDIA_DIR= to appropriate folder path
        if SPACE_TIMER_HOURS > 0:
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
        file_name = getVideoName(VIDEO_DIR, VIDEO_PREFIX, VIDEO_NUM_ON, videoNumCounter)
        takeVideo(file_name, VIDEO_FILE_SEC,
                  VIDEO_REPEAT_WIDTH,
                  VIDEO_REPEAT_HEIGHT,
                  VIDEO_FPS
                 )
        timeUsed = (datetime.datetime.now() - videoStartTime).total_seconds()
        timeRemaining = (VIDEO_SESSION_MIN * 60 - timeUsed) / 60.0
        videoCount += 1
        if VIDEO_NUM_ON:
            videoNumCounter += 1
            if VIDEO_NUM_MAX > 0:
                if videoNumCounter - VIDEO_NUM_START > VIDEO_NUM_MAX:
                    if VIDEO_NUM_RECYCLE_ON:
                        videoNumCounter = VIDEO_NUM_START
                        logging.info(
                            "Restart Numbering: VIDEO_NUM_RECYCLE_ON=%s "
                            "and VIDEO_NUM_MAX=%i Exceeded",
                            VIDEO_NUM_RECYCLE_ON,
                            VIDEO_NUM_MAX,
                        )
                    else:
                        keepRecording = False
                        logging.info(
                            "Exit since VIDEO_NUM_RECYCLE_ON=%s "
                            "and VIDEO_NUM_MAX=%i Exceeded  %i Videos Recorded",
                            VIDEO_NUM_RECYCLE_ON,
                            VIDEO_NUM_MAX,
                            videoCount,
                        )
                logging.info("Recorded %i of %i Videos", videoCount, VIDEO_NUM_MAX)
            else:
                logging.info(
                    "Recorded %i Videos  VIDEO_NUM_MAX=%i 0=Continuous",
                    videoCount,
                    VIDEO_NUM_MAX,
                )
        else:
            logging.info(
                "Progress: %i Videos Recorded in Folder %s", videoCount, VIDEO_DIR
            )
        if VIDEO_SESSION_MIN > 0:
            if timeUsed > VIDEO_SESSION_MIN * 60:
                keepRecording = False
                errorText = (
                    "Stop Recording Since VIDEO_SESSION_MIN=%i minutes Exceeded \n",
                    VIDEO_SESSION_MIN,
                )
                logging.warning(errorText)
                sys.stdout.write(errorText)
            else:
                logging.info(
                    "Remaining Time %.1f of %i minutes",
                    timeRemaining,
                    VIDEO_SESSION_MIN,
                )
        else:
            videoStartTime = datetime.datetime.now()
    logging.info("Exit: %i Videos Recorded in Folder %s", videoCount, VIDEO_DIR)


# ------------------------------------------------------------------------------
def timolo():
    """
    Main motion and or motion tracking
    initialization and logic loop
    """

    cam_tl_pos = 0  # PANTILT_SEQ_STOPS List Start position of pantilt
    pan_x, tilt_y = PANTILT_SEQ_STOPS[cam_tl_pos]
    dotCount = 0
    checkMediaPaths()
    timelapse_num_count = 0
    motion_num_count = 0

    tlstr = ""  # Used to display if timelapse is selected
    mostr = ""  # Used to display if motion is selected
    moCnt = "non"
    tlCnt = "non"

    day_mode = False  # Keep track of night and day based on dayPixAve

    motionFound = False
    take_timelapse = True
    stop_timelapse = False
    takeMotion = True
    stopMotion = False

    # Initialize some Timers
    pix_ave_timer = datetime.datetime.now()
    pantilt_seq_timer = datetime.datetime.now()
    motion_force_timer = datetime.datetime.now()
    timelapseExitStart = datetime.datetime.now()
    startTL = getSchedStart(TIMELAPSE_START_AT)
    startMO = getSchedStart(MOTION_START_AT)
    trackLen = 0.0
    if SPACE_TIMER_HOURS > 0:
        lastSpaceCheck = datetime.datetime.now()
    if TIMELAPSE_ON:
        tlstr = "TimeLapse"
        # Check if timelapse subDirs reqd and create one if non exists
        tlPath = subDirChecks(
            TIMELAPSE_SUBDIR_MAX_HOURS,
            TIMELAPSE_SUBDIR_MAX_FILES,
            TIMELAPSE_DIR,
            TIMELAPSE_PREFIX,
        )
        if TIMELAPSE_NUM_ON:
            timelapse_num_count = getCurrentCount(NUM_PATH_TIMELAPSE, TIMELAPSE_NUM_START)
            tlCnt = str(timelapse_num_count)
    else:
        logging.warning("Timelapse is Surpressed per TIMELAPSE_ON=%s", TIMELAPSE_ON)
        stop_timelapse = True
    if MOTION_TRACK_ON:
        logging.info("Start picamera2 VideoStream Thread ...")
        if MOTION_TRACK_QUICK_PIC_ON:
            logging.info(f"Motion Track Mode: MOTION_TRACK_QUICK_PIC_ON= {MOTION_TRACK_QUICK_PIC_ON}")
        elif MOTION_TRACK_MINI_TL_ON:
            logging.info(f"Motion Track Mode: MOTION_TRACK_MINI_TL_ON= {MOTION_TRACK_MINI_TL_ON}")
        elif MOTION_TRACK_PANTILT_SEQ_ON:
            logging.info(f"Motion Track Mode: MOTION_TRACK_PANTILT_SEQ_ON= {MOTION_TRACK_PANTILT_SEQ_ON}")
        elif MOTION_VIDEO_ON:
            logging.info(f"Motion Track Mode: MOTION_VIDEO_ON= {MOTION_VIDEO_ON}")
        else:
            logging.info(f"Motion Track Mode: STILL IMAGE")

        vs = CamStream(size=(STREAM_WIDTH, STREAM_HEIGHT),
                       vflip=IMAGE_VFLIP,
                       hflip=IMAGE_HFLIP).start()
        mostr = "Motion Tracking"
        # Check if motion subDirs required and
        # create one if required and non exists
        mo_path = subDirChecks(
            MOTION_SUBDIR_MAX_HOURS, MOTION_SUBDIR_MAX_FILES, MOTION_DIR, MOTION_PREFIX
        )
        if MOTION_NUM_ON:
            motion_num_count = getCurrentCount(NUM_PATH_MOTION, MOTION_NUM_START)
            moCnt = str(motion_num_count)
        trackTimeout = time.time()
        trackTimer = TRACK_TIMEOUT
        startPos = []
        startTrack = False
        image_1 = vs.read()
        image_2 = vs.read()
        pixAve = getStreamPixAve(image_2)
        grayimage_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
        day_mode = checkIfDayStream(day_mode, image_2)
    else:
        vs = CamStream(size=(STREAM_WIDTH, STREAM_HEIGHT),
                       vflip=IMAGE_VFLIP,
                       hflip=IMAGE_HFLIP).start()
        time.sleep(0.5)
        image_2 = vs.read()  # use video stream to check for pixAve & day_mode
        pixAve = getStreamPixAve(image_2)
        day_mode = checkIfDayStream(day_mode, image_2)
        vs.stop()
        time.sleep(STREAM_STOP_SEC)
        logging.info(
            "Motion Tracking is Surpressed per MOTION_TRACK_ON=%s",
            MOTION_TRACK_ON,
        )
        stopMotion = True
    if TIMELAPSE_ON and MOTION_TRACK_ON:
        tlstr = " and " + tlstr

    if LOG_TO_FILE_ON:
        logging.info(f"LOG_TO_FILE_ON= {LOG_TO_FILE_ON} Logging to Console Disabled.")
        logging.info(f"Sending Console Messages to {log_file_path}")
        logging.info(f"Entering Loop for {mostr}{lstr}")
    else:
        if PLUGIN_ON:
            logging.info("plugin %s - Start %s%s Loop ...", PLUGIN_NAME, mostr, tlstr)
        else:
            logging.info(f"Start {mostr}{tlstr} Loop ... ctrl-c Exits")
    if MOTION_TRACK_ON and not checkSchedStart(startMO):
        logging.info('Motion Track: MOTION_START_AT = "%s"', MOTION_START_AT)
        logging.info("Motion Track: Sched Start Set For %s  Please Wait ...", startMO)
    if TIMELAPSE_ON and not checkSchedStart(startTL):
        logging.info('Timelapse   : TIMELAPSE_START_AT = "%s"', TIMELAPSE_START_AT)
        logging.info("Timelapee   : Sched Start Set For %s  Please Wait ...", startTL)
    # Check to make sure PANTILT_ON is enabled if required.
    if PANTILT_SEQ_ON and not PANTILT_ON:
        logging.warning(
            "PANTILT_SEQ_ON=True but PANTILT_ON=False (Suggest you Enable PANTILT_ON=True)"
        )
    if PANO_ON and not PANTILT_ON:
        logging.warning(
            "PANO_ON=True but PANTILT_ON=False (Suggest you Enable PANTILT_ON=True)"
        )
    if (MOTION_TRACK_PANTILT_SEQ_ON and MOTION_TRACK_ON) and not PANTILT_ON:
        logging.warning(
            "MOTION_TRACK_PANTILT_SEQ_ON=True but PANTILT_ON=False (Suggest you Enable PANTILT_ON=True)"
        )
    first_pano = True  # Force a pano sequence on startup
    first_timelapse = True  # Force a timelapse on startup
    while True:  # Start main program Loop.
        motionFound = False
        if (MOTION_TRACK_ON
            and (not MOTION_NUM_RECYCLE_ON)
            and (motion_num_count > MOTION_NUM_START + MOTION_NUM_MAX)
            and (not stopMotion)):
            logging.warning(
                "MOTION_NUM_RECYCLE_ON=%s and motion_num_count %i Exceeds %i",
                MOTION_NUM_RECYCLE_ON,
                motion_num_count,
                MOTION_NUM_START + MOTION_NUM_MAX,
            )
            logging.warning("Suppressing Further Motion Tracking")
            logging.warning(
                "To Reset: Change %s Settings or Archive Images", CONFIG_FILENAME
            )
            logging.warning(
                f"Then Delete {NUM_PATH_MOTION} and Restart {PROG_NAME} \n")
            takeMotion = False
            stopMotion = True
        if stop_timelapse and stopMotion and not PANTILT_SEQ_ON and not PANO_ON and not VIDEO_REPEAT_ON:
            logging.warning(
                "NOTICE: Motion, Timelapse, pantilt_seq, Pano and Video Repeat are Disabled"
            )
            logging.warning(
                "per Num Recycle=False and "
                "Max Counter Reached or TIMELAPSE_EXIT_SEC Settings"
            )
            logging.warning(
                "Change %s Settings or Archive/Save Media Then", CONFIG_FILENAME
            )
            logging.warning("Delete appropriate .dat File(s) to Reset Counter(s)")
            logging.warning(f"Exiting {PROG_NAME} {PROG_VER} \n")
            sys.exit(1)
        # if required check free disk space and delete older files (jpg)
        if SPACE_TIMER_HOURS > 0:
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
        # check the timer for measuring pixel average of stream image frame
        pix_ave_timer, take_pix_ave = checkTimer(pix_ave_timer, IMAGE_PIX_AVE_TIMER_SEC)
        # use image_2 to check day_mode as image_1 may be average
        # that changes slowly, and image_1 may not be updated
        if take_pix_ave:
            pixAve = getStreamPixAve(image_2)
            pixAve = getStreamPixAve(image_2)
            day_mode = checkIfDayStream(day_mode, image_2)
            if day_mode != checkIfDayStream(day_mode, image_2):
                day_mode = not day_mode
        if MOTION_TRACK_ON:
            if day_mode != checkIfDayStream(day_mode, image_2):
                day_mode = not day_mode
                image_2 = vs.read()
                image_1 = image_2
            else:
                image_2 = vs.read()
        elif TIMELAPSE_ON:
            vs = CamStream(size=(STREAM_WIDTH, STREAM_HEIGHT),
                           vflip=IMAGE_VFLIP,
                           hflip=IMAGE_HFLIP).start()
            time.sleep(0.5)
            image_2 = vs.read()  # use video stream to check for day_mode
            vs.stop()
            time.sleep(STREAM_STOP_SEC)
        if not day_mode and TIMELAPSE_ON:
            time.sleep(0.02)  # short delay to aviod high cpu usage at night
        # Don't take images if IMAGE_NO_NIGHT_SHOTS
        # or IMAGE_NO_DAY_SHOTS settings are True
        if not timeToSleep(day_mode):
            # Check if it is time for pantilt sequence
            if PANTILT_ON and PANTILT_SEQ_ON:
                pantilt_seq_timer, take_pantilt_sequence = checkTimer(
                    pantilt_seq_timer, PANTILT_SEQ_TIMER_SEC
                )
                if take_pantilt_sequence:
                    if MOTION_TRACK_ON:
                        vs.stop()
                        time.sleep(STREAM_STOP_SEC)
                    seq_prefix = PANTILT_SEQ_IMAGE_PREFIX + IMAGE_NAME_PREFIX
                    seq_num_count = getCurrentCount(
                        NUM_PATH_PANTILT_SEQ, PANTILT_SEQ_NUM_START
                    )
                    file_name = getImagefile_name(PANTILT_SEQ_IMAGES_DIR,
                                                seq_prefix,
                                                PANTILT_SEQ_NUM_ON,
                                                seq_num_count,
                                                )
                    seq_num_count = takePantiltSequence(file_name, day_mode,
                                                        seq_num_count,
                                                        NUM_PATH_PANTILT_SEQ,
                                                        image_2
                                                        )
                    if MOTION_TRACK_ON:
                        logging.info("Restart picamera2 VideoStream Thread ...")
                        vs = CamStream(size=(STREAM_WIDTH, STREAM_HEIGHT),
                                       vflip=IMAGE_VFLIP,
                                       hflip=IMAGE_HFLIP).start()
                        time.sleep(1)  # Allow camera to warm up and stream to start
                    next_seq_time = pantilt_seq_timer + datetime.timedelta(
                        seconds=PANTILT_SEQ_TIMER_SEC
                    )
                    next_seq_at = "%02d:%02d:%02d" % (
                        next_seq_time.hour,
                        next_seq_time.minute,
                        next_seq_time.second,
                    )
                    logging.info(
                        "Next Pantilt Sequence in %i seconds at %s  Waiting ...",
                        PANTILT_SEQ_TIMER_SEC, next_seq_at
                    )
            # Process Timelapse events per timers
            if TIMELAPSE_ON and checkSchedStart(startTL):
                # Check for a scheduled date/time to start timelapse
                if first_timelapse:
                    timelapse_timer = datetime.datetime.now()
                    first_timelapse = False
                    take_timelapse = True
                else:
                    timelapse_timer, take_timelapse = checkTimer(
                        timelapse_timer, TIMELAPSE_TIMER_SEC
                    )
                if (not stop_timelapse) and take_timelapse and TIMELAPSE_EXIT_SEC > 0:
                    if (
                        datetime.datetime.now() - timelapseExitStart
                    ).total_seconds() > TIMELAPSE_EXIT_SEC:
                        logging.info(
                            "TIMELAPSE_EXIT_SEC=%i Exceeded.", TIMELAPSE_EXIT_SEC
                        )
                        logging.info("Suppressing Further Timelapse Images")
                        logging.info(
                            "To RESET: Restart %s to Restart "
                            "TIMELAPSE_EXIT_SEC Timer. \n",
                            PROG_NAME,
                        )
                        # Suppress further timelapse images
                        take_timelapse = False
                        stop_timelapse = True
                if (
                    (not stop_timelapse)
                    and TIMELAPSE_NUM_ON
                    and (not TIMELAPSE_NUM_RECYCLE_ON)
                ):
                    if TIMELAPSE_NUM_MAX > 0 and timelapse_num_count > (
                        TIMELAPSE_NUM_START + TIMELAPSE_NUM_MAX
                    ):
                        logging.warning(
                            "TIMELAPSE_NUM_RECYCLE_ON=%s and Counter=%i Exceeds %i",
                            TIMELAPSE_NUM_RECYCLE_ON,
                            timelapse_num_count,
                            TIMELAPSE_NUM_START + TIMELAPSE_NUM_MAX,
                        )
                        logging.warning("Suppressing Further Timelapse Images")
                        logging.warning(
                            "To RESET: Change %s Settings or Archive Images",
                            CONFIG_FILENAME,
                        )
                        logging.warning(
                            f"Then Delete {NUM_PATH_TIMELAPSE} and Restart {PROG_NAME} \n")
                        # Suppress further timelapse images
                        take_timelapse = False
                        stop_timelapse = True
                if take_timelapse and (not stop_timelapse):
                    if PLUGIN_ON:
                        if TIMELAPSE_EXIT_SEC > 0:
                            exitSecProgress = (
                                datetime.datetime.now() - timelapseExitStart
                            ).total_seconds()
                            logging.info(
                                "%s Sched TimeLapse  day_mode=%s  Timer=%i sec"
                                "  ExitSec=%i/%i Status",
                                PLUGIN_NAME,
                                day_mode,
                                TIMELAPSE_TIMER_SEC,
                                exitSecProgress,
                                TIMELAPSE_EXIT_SEC,
                            )
                        else:
                            logging.info(
                                "%s Sched TimeLapse  day_mode=%s"
                                "  Timer=%i sec  ExitSec=%i 0=Continuous",
                                PLUGIN_NAME,
                                day_mode,
                                TIMELAPSE_TIMER_SEC,
                                TIMELAPSE_EXIT_SEC,
                            )
                    else:
                        if TIMELAPSE_EXIT_SEC > 0:
                            exitSecProgress = (
                                datetime.datetime.now() - timelapseExitStart
                            ).total_seconds()
                            logging.info(
                                "Sched TimeLapse  day_mode=%s  Timer=%i sec"
                                "  ExitSec=%i/%i Status",
                                day_mode,
                                TIMELAPSE_TIMER_SEC,
                                exitSecProgress,
                                TIMELAPSE_EXIT_SEC,
                            )
                        else:
                            logging.info(
                                "Sched TimeLapse  day_mode=%s  Timer=%i sec"
                                "  ExitSec=%i 0=Continuous",
                                day_mode,
                                TIMELAPSE_TIMER_SEC,
                                TIMELAPSE_EXIT_SEC,
                            )
                    tl_prefix = TIMELAPSE_PREFIX + IMAGE_NAME_PREFIX
                    file_name = getImagefile_name(
                        tlPath, tl_prefix, TIMELAPSE_NUM_ON, timelapse_num_count
                    )

                    if MOTION_TRACK_ON:
                        logging.info("Stop Motion Tracking Picamera2 VideoStream ...")
                        vs.stop()
                        time.sleep(STREAM_STOP_SEC)
                    # Time to take a Day or Night Time Lapse Image
                    takeImage(file_name, image_2)
                    timelapse_num_count = postImageProcessing(
                        TIMELAPSE_NUM_ON,
                        TIMELAPSE_NUM_START,
                        TIMELAPSE_NUM_MAX,
                        timelapse_num_count,
                        TIMELAPSE_NUM_RECYCLE_ON,
                        NUM_PATH_TIMELAPSE,
                        file_name,
                        day_mode,
                    )
                    saveRecent(
                        TIMELAPSE_RECENT_MAX, TIMELAPSE_RECENT_DIR, file_name, tl_prefix
                    )

                    if MOTION_TRACK_ON:
                        logging.info("Restart picamera2 VideoStream Thread ...")
                        vs = CamStream(size=(STREAM_WIDTH, STREAM_HEIGHT),
                                       vflip=IMAGE_VFLIP,
                                       hflip=IMAGE_HFLIP).start()
                        time.sleep(1)  # Allow camera to warm up and stream to start
                    if TIMELAPSE_MAX_FILES > 0:
                        deleteOldFiles(TIMELAPSE_MAX_FILES, TIMELAPSE_DIR, tl_prefix)

                    tlPath = subDirChecks(
                        TIMELAPSE_SUBDIR_MAX_HOURS,
                        TIMELAPSE_SUBDIR_MAX_FILES,
                        TIMELAPSE_DIR,
                        TIMELAPSE_PREFIX,
                    )
                    next_timelapse_time = timelapse_timer + datetime.timedelta(
                        seconds=TIMELAPSE_TIMER_SEC
                    )
                    next_timelapse_at = "%02d:%02d:%02d" % (
                        next_timelapse_time.hour,
                        next_timelapse_time.minute,
                        next_timelapse_time.second,
                    )
                    logging.info("Next Timelapse at %s  Waiting ...", next_timelapse_at)
                    pantiltGoHome()
            # Monitor for motion tracking events
            # and trigger selected action eg image, quick pic, video, mini TL, pantilt
            if (
                MOTION_TRACK_ON
                and checkSchedStart(startMO)
                and takeMotion
                and (not stopMotion)
            ):
                # IMPORTANT - Night motion tracking may not work very well
                #             due to long exposure times and low light
                image_2 = vs.read()
                grayimage_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY)
                movePoint1 = getMotionTrackPoint(grayimage_1, grayimage_2)
                grayimage_1 = grayimage_2
                if movePoint1 and not startTrack:
                    startTrack = True
                    trackTimeout = time.time()
                    startPos = movePoint1
                image_2 = vs.read()
                grayimage_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2GRAY)
                movePoint2 = getMotionTrackPoint(grayimage_1, grayimage_2)
                if movePoint2 and startTrack:  # Two sets of movement required
                    trackLen = trackMotionDistance(startPos, movePoint2)
                    # wait until track well started
                    if trackLen > TRACK_TRIG_LEN_MIN:
                        # Reset tracking timer object moved
                        trackTimeout = time.time()
                        if MOTION_TRACK_INFO_ON:
                            logging.info(
                                "Track Progress From(%i,%i) To(%i,%i) trackLen=%i/%i px",
                                startPos[0],
                                startPos[1],
                                movePoint2[0],
                                movePoint2[1],
                                trackLen,
                                TRACK_TRIG_LEN,
                            )
                    # Track length triggered
                    if trackLen >= TRACK_TRIG_LEN:
                        # reduce chance of two objects at different positions
                        if trackLen >= TRACK_TRIG_LEN_MAX:
                            motionFound = False
                            if MOTION_TRACK_INFO_ON:
                                logging.info(
                                    "TrackLen %i px Exceeded %i px Max Trig Len Allowed.",
                                    trackLen,
                                    TRACK_TRIG_LEN_MAX,
                                )
                        else:
                            motionFound = True
                            if PLUGIN_ON:
                                logging.info(
                                    "%s Motion Triggered Start(%i,%i)"
                                    "  End(%i,%i) trackLen=%.i/%i px",
                                    PLUGIN_NAME,
                                    startPos[0],
                                    startPos[1],
                                    movePoint2[0],
                                    movePoint2[1],
                                    trackLen,
                                    TRACK_TRIG_LEN,
                                )
                            else:
                                logging.info(
                                    "Motion Triggered Start(%i,%i)"
                                    "  End(%i,%i) trackLen=%i/%i px",
                                    startPos[0],
                                    startPos[1],
                                    movePoint2[0],
                                    movePoint2[1],
                                    trackLen,
                                    TRACK_TRIG_LEN,
                                )
                            print("")
                        image_1 = vs.read()
                        image_2 = image_1
                        grayimage_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
                        grayimage_2 = grayimage_1
                        startTrack = False
                        startPos = []
                        trackLen = 0.0
                # Track timed out
                if (time.time() - trackTimeout > trackTimer) and startTrack:
                    image_1 = vs.read()
                    image_2 = image_1
                    grayimage_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
                    grayimage_2 = grayimage_1
                    if MOTION_TRACK_ON and MOTION_TRACK_INFO_ON:
                        logging.info(
                            "Track Timer %.2f sec Exceeded. Reset Track", trackTimer
                        )
                    startTrack = False
                    startPos = []
                    trackLen = 0.0
                if MOTION_FORCE_SEC > 0:
                    motion_force_timer, motion_force_start = checkTimer(
                        motion_force_timer, MOTION_FORCE_SEC
                    )
                else:
                    motion_force_start = False
                if motion_force_start:
                    image_1 = vs.read()
                    image_2 = image_1
                    grayimage_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
                    grayimage_2 = grayimage_1
                    logging.info(
                        "No Motion Detected for %s minutes. "
                        "Taking Forced Motion Image.",
                        (MOTION_FORCE_SEC / 60),
                    )
                if motionFound or motion_force_start:
                    motion_prefix = MOTION_PREFIX + IMAGE_NAME_PREFIX
                    file_name = getImagefile_name(
                        mo_path, motion_prefix, MOTION_NUM_ON, motion_num_count
                    )
                    vs.stop()
                    time.sleep(STREAM_STOP_SEC)

                    # Save stream image frame to capture movement quickly
                    if MOTION_TRACK_QUICK_PIC_ON:
                        takeMotionQuickImage(image_2, file_name)
                        motion_num_count = postImageProcessing(
                            MOTION_NUM_ON,
                            MOTION_NUM_START,
                            MOTION_NUM_MAX,
                            motion_num_count,
                            MOTION_NUM_RECYCLE_ON,
                            NUM_PATH_MOTION,
                            file_name,
                            day_mode,
                        )
                        saveRecent(
                            MOTION_RECENT_MAX,
                            MOTION_RECENT_DIR,
                            file_name,
                            motion_prefix,
                        )
                    # Save a series of images per settings (no pantilt)
                    elif MOTION_TRACK_MINI_TL_ON and day_mode:
                        takeMiniTimelapse(
                            mo_path,
                            motion_prefix,
                            MOTION_NUM_ON,
                            motion_num_count,
                            day_mode,
                            image_2)

                    # Move camera pantilt through specified positions and take images
                    elif (MOTION_TRACK_ON and PANTILT_ON and MOTION_TRACK_PANTILT_SEQ_ON):
                        motion_num_count = takePantiltSequence(file_name, day_mode,
                                                               motion_num_count,
                                                               NUM_PATH_MOTION,
                                                               image_2)
                        pantiltGoHome()
                    elif MOTION_VIDEO_ON:
                        file_name = getVideoName(
                            MOTION_PATH, motion_prefix, MOTION_NUM_ON, motion_num_count
                        )
                        takeVideo(
                            file_name,
                            MOTION_VIDEO_TIMER_SEC,
                            MOTION_VIDEO_WIDTH,
                            MOTION_VIDEO_HEIGHT,
                            MOTION_VIDEO_FPS,
                        )
                        if MOTION_NUM_ON:
                            motion_num_count += 1
                            writeCounter(motion_num_count, NUM_PATH_MOTION)
                    else:
                        takeImage(file_name, image_2)
                        motion_num_count = postImageProcessing(
                            MOTION_NUM_ON,
                            MOTION_NUM_START,
                            MOTION_NUM_MAX,
                            motion_num_count,
                            MOTION_NUM_RECYCLE_ON,
                            NUM_PATH_MOTION,
                            file_name,
                            day_mode,
                        )

                        saveRecent(
                            MOTION_RECENT_MAX,
                            MOTION_RECENT_DIR,
                            file_name,
                            motion_prefix,
                        )

                    vs = CamStream(size=(STREAM_WIDTH, STREAM_HEIGHT),
                                         vflip=IMAGE_VFLIP,
                                         hflip=IMAGE_HFLIP).start()
                    time.sleep(1)
                    image_1 = vs.read()
                    image_2 = image_1
                    grayimage_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2GRAY)
                    grayimage_2 = grayimage_1
                    trackLen = 0.0
                    trackTimeout = time.time()
                    startPos = []
                    startTrack = False
                    mo_path = subDirChecks(
                        MOTION_SUBDIR_MAX_HOURS,
                        MOTION_SUBDIR_MAX_FILES,
                        MOTION_DIR,
                        MOTION_PREFIX,
                    )
                    if TIMELAPSE_ON:
                        logging.info("Waiting for Next Timelapse or Motion Tracking Event ...")                       
                    else:
                       logging.info("Waiting for Next Motion Tracking Event ...")
            # Take panoramic images and stitch together if possible per settings
            if PANTILT_ON and PANO_ON:
                # force a pano on first startup then go by timer.
                if first_pano:
                    first_pano = False
                    start_pano = True
                    pano_seq_num = getCurrentCount(NUM_PATH_PANO, PANO_NUM_START)
                    pano_timer = datetime.datetime.now()
                else:
                    # Check if pano timer expired and if so start a pano sequence
                    pano_timer, start_pano = checkTimer(pano_timer, PANO_TIMER_SEC)
                if start_pano:
                    if MOTION_TRACK_ON:
                        logging.info("Stop Motion Tracking picamera2 VideoStream ...")
                        vs.stop()
                        time.sleep(STREAM_STOP_SEC)
                    pano_seq_num = takePano(pano_seq_num, day_mode, image_2)
                    if MOTION_TRACK_ON:
                        logging.info("Restart Motion Tracking picamera2 VideoStream Thread ...")
                        vs = CamStream(size=(STREAM_WIDTH, STREAM_HEIGHT),
                                       vflip=IMAGE_VFLIP,
                                       hflip=IMAGE_HFLIP).start()
                        time.sleep(1)
                    next_pano_time = pano_timer + datetime.timedelta(
                        seconds=PANO_TIMER_SEC
                    )
                    next_pano_at = "%02d:%02d:%02d" % (
                        next_pano_time.hour,
                        next_pano_time.minute,
                        next_pano_time.second,
                    )
                    logging.info("Next Pano at %s  Waiting ...", next_pano_at)

                if motionFound and motionCode:
                    # ===========================================
                    # Put your user code in userMotionCode() function
                    # In the File user_motion_code.py
                    # ===========================================
                    try:
                        user_motion_code.userMotionCode(file_name)
                    except ValueError:
                        logging.error(
                            "Problem running userMotionCode function from File %s",
                            user_motion_filepath,
                        )


# ------------------------------------------------------------------------------
if __name__ == "__main__":

    checkConfig()

    if PANTILT_ON:
        logging.info("Camera Pantilt Hardware is %s", pantilt_is)
    if PLUGIN_ON:
        logging.info(
            "Start pi-timolo per %s and plugins/%s.py Settings",
            config_file_path,
            PLUGIN_NAME,
        )
    else:
        logging.info("Start pi-timolo per %s Settings", config_file_path)
    if not VERBOSE_ON:
        print("NOTICE: Logging Disabled per VERBOSE_ON=False  ctrl-c Exits")
    try:
        pantiltGoHome()
        if VIDEO_REPEAT_ON:
            videoRepeat()
        else:
            timolo()
    except KeyboardInterrupt:
        print("")
        pantiltGoHome()  # Ensure pantilt is returned to home position
        if VERBOSE_ON:
            logging.info("\nUser Pressed Keyboard ctrl-c")
            logging.info(f"Exiting {PROG_NAME} {PROG_VER}")
        else:
            sys.stdout.write("User Pressed Keyboard ctrl-c \n")
            sys.stdout.write(f"Exiting {PROG_NAME} {PROG_VER} \n")
    try:
        if PLUGIN_ON:
            if os.path.isfile(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.isfile(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
    except OSError as err:
        logging.warning("Failed To Remove File %s - %s", pluginCurrentpyc, err)
        sys.exit(1)
    print("Wait ...")
