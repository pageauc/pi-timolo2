# User Configuration variable settings for pitimolo
# Purpose - Motion Detection Security Cam
# Updated - 15-Feb-2025
# Done by - Claude Pageau

CONFIG_TITLE = "pi-timolo2 ver 13.14 Custom Settings"
CONFIG_FILENAME  = "config.py"
CONFIG_VERSION = 13.14  # Version of this file used for compatiblity checking

#======================================
#   timolo2.py Settings
#======================================

# Logging and Debug Settings
# --------------------------
# Note - Set VERBOSE_ON to False if script is run in background or from /etc/rc.local

PLUGIN_ON = False       # Default= False True reads customized settings from a custom.py file
PLUGIN_NAME = "shopcam" # Specify filename in plugins subfolder without .py extension per below
                        # TLlong, TLshort, secfast, secstill, strmvid, secvid,
                        # secQTL, shopcam, dashcam, slowmo, TLpan, pano

VERBOSE_ON = True       # Default= True Sends logging Info to Console. False if running script as daeman
LOG_TO_FILE_ON = False  # Default= False True logs diagnostic data to a disk file for review
DEBUG_ON = False        # Default= False True= DEBUG_ON mode returns pixel average data for tuning

# Image Settings
# --------------
IMAGE_NAME_PREFIX = 'cam1-'  # Default= 'cam1-' for all image file names. Eg garage-
IMAGE_WIDTH = 1280           # Default= 1280 Full Size Image Width in px
IMAGE_HEIGHT = 768           # Default= 720  Full Size Image Height in px
IMAGE_FORMAT = ".jpg"        # Default= ".jpg"  image Formats .jpeg .png .gif .bmp
IMAGE_JPG_QUAL = 95          # Default= 95 jpg Encoder Quality 1(low)-100(high) 0=85
IMAGE_ROTATION = None        # Default= None  Rotates image. Valid values: None, 0, 90, 180, 270
IMAGE_VFLIP = True           # Default= False True Flips image Vertically
IMAGE_HFLIP = True           # Default= False True Flips image Horizontally
IMAGE_GRAYSCALE = False      # Default= False True=Save image as grayscale False=Color
IMAGE_PREVIEW = False        # Default= False True=Preview image on connected RPI Monitor or Display
IMAGE_PIX_AVE_TIMER_SEC = 15 # Default= 15 Interval seconds for checking pixAverage Readings (reduces cpu usage)
IMAGE_NO_NIGHT_SHOTS = False # Default= False True=No Night Images (Motion or Timelapse)
IMAGE_NO_DAY_SHOTS = False   # Default= False True=No Day Images (Motion or Timelapse)
IMAGE_SHOW_STREAM = False    # Default= False True=Show video stream motion tracking area on full size image.
IMAGE_SHOW_EXIF_ON = False   # Default= False True=Show image Exif metadata
 
 # Use to Align Camera for motion tracking.  Set to False when Alignment complete.
STREAM_WIDTH = 320           # Default= 320  Width of motion tracking stream detection area
STREAM_HEIGHT = 240          # Default= 240  Height of motion tracking stream detection area
STREAM_FPS = 20              # Default= 20 fps PiVideoStream setting.  Single core RPI suggest 15 fps
STREAM_STOP_SEC = 4          # Default= 0.7 Allow time to stop video stream thread to release camera

# Note see STREAM_FPS variable below to set motion video stream framerate for stream size above

# Date/Time Settings for Displaying info Directly on Images
# ---------------------------------------------------------
SHOW_DATE_ON_IMAGE = True    # Default= True False=Do Not display date/time text on images
SHOW_TEXT_FONT_SIZE = 18     # Default= 18 Size of image Font in pixel height
SHOW_TEXT_BOTTOM = True      # Default= True Bottom Location of image Text False= Top
SHOW_TEXT_WHITE = True       # Default= True White Colour of image Text False= Black
SHOW_TEXT_WHITE_NIGHT = True # Default= True Changes night text to white.  Useful if night needs white text instead of black

# Low Light  Settings
# -------------------
DARK_MAX_EXP_SEC = 6.0   # picamera V1 default is 6.0 sec. V2 is 10 Sec
DARK_START_PXAVE = 32    # pxAve transition point between dark and light.
DARK_GAIN = 10.0         # analogue_gain (ISO/100) for dark mode.  Max is 16

# Time Lapse Settings
# -------------------
TIMELAPSE_ON = True           # Default= False True=Turn timelapse On, False=Off
TIMELAPSE_PREFIX = "tl-"      # Default= "tl-" Prefix for All timelapse images with this prefix
TIMELAPSE_TIMER_SEC = 300     # Default= 120 (2 min) Seconds between timelapse images.
TIMELAPSE_DIR = "media/timelapse" # Default= "media/timelapse"  Storage Folder Path for Time Lapse Image Storage
TIMELAPSE_RECENT_DIR = "media/recent/timelapse"  # Default= "media/recent/timelapse"  location of timelapse recent files
TIMELAPSE_RECENT_MAX = 200    # Default= 200 0=Off or specify number of most recent files in TIMELAPSE_RECENT_DIR
TIMELAPSE_START_AT = ""       # Default= "" Off or specify date/time to Start Sequence Eg "01-dec-2019 08:00:00" or "20:00:00"
TIMELAPSE_NUM_ON = True       # Default= True filenames Sequenced by Number False=filenames by date/time
TIMELAPSE_NUM_RECYCLE_ON = True # Default= True Restart Numbering at NumStart  False= Surpress Timelapse at NumMax
TIMELAPSE_NUM_START = 1000    # Default= 1000 Start of timelapse number sequence
TIMELAPSE_NUM_MAX = 2000      # Default= 2000 Max number of timelapse images desired. 0=Continuous
TIMELAPSE_EXIT_SEC = 0        # Default= 0 seconds Surpress Timelapse after specified Seconds  0=Continuous
TIMELAPSE_MAX_FILES = 0       # Default= 0 0=Off or specify MaxFiles to maintain then oldest are deleted  Default=0 (Off)
TIMELAPSE_SUBDIR_MAX_FILES = 0 # Default= 0 0=Off or specify MaxFiles - Creates New dated sub-folder if MaxFiles exceeded
TIMELAPSE_SUBDIR_MAX_HOURS = 0 # Default= 0 0=Off or specify MaxHours - Creates New dated sub-folder if MaxHours exceeded

# Motion Track Settings
# ---------------------
MOTION_TRACK_ON = True         # Default= True True=Turns Motion Detect On, False=Off
MOTION_TRACK_INFO_ON = False   # Default= True False= Hide detailed track progress logging messages
MOTION_TRACK_TIMEOUT_SEC = 0.3 # Default= 0.3 seconds Resets Track if no movement tracked
MOTION_TRACK_TRIG_LEN = 50     # Default= 75 px Length of motion track to Trigger motionFound
MOTION_TRACK_MIN_AREA = 100    # Default= 100 sq px  Minimum Area required to start tracking

# Motion Settings
# ---------------
MOTION_PREFIX = "mo-"        # Default= "mo-" Prefix for all Motion Detect images
MOTION_DIR = "media/motion"  # Default= "media/motion"  Folder Path for Motion Detect Image Storage
MOTION_RECENT_DIR = "media/recent/motion"  # Default= "media/recent/motion"  Location of motion Recent files
MOTION_RECENT_MAX = 200      # Default= 200 0=Off or specify number of recent files in MOTION_RECENT_DIR
MOTION_START_AT = ""         # Default= "" Off or Specify date/time to Start Sequence Eg "01-jan-20018 08:00:00" or "20:00:00"
MOTION_NUM_ON = True         # Default= True filenames by sequenced Number  False= filenames by date/time
MOTION_NUM_RECYCLE_ON = True # Default= True when NumMax reached restart at NumStart instead of exiting
MOTION_NUM_START = 1000      # Default= 1000 Start 0f motion number sequence
MOTION_NUM_MAX  = 2000       # Default= 2000 Max number of motion images desired. 0=Continuous
MOTION_FORCE_SEC = 3600      # Default= 3600 seconds (1 hr) OFF=0  Force an image if no Motion Detected in specified seconds.
MOTION_SUBDIR_MAX_FILES = 0  # Default= 0 0=Off or specify Max Files to create new sub-folder if MAX FILES exceeded
MOTION_SUBDIR_MAX_HOURS = 0  # Default= 0 0=Off or specify Max Hrs to create new sub-folder if MAX HOURS exceeded

# Default motion tracking action is to take image per IMAGE_ settings above
# with all MOTION_...._ON options below set to False.
# You can override default action by enabling ONE of the FOUR options below.
# ---------------------------------------------------------------------------------
MOTION_TRACK_QUICK_PIC_ON = False   # Default= False True= Grab single stream frame rather than stopping stream to take full size image
MOTION_TRACK_QUICK_PIC_BIGGER = 3.0 # Default= 3.0 multiply size of QuickPic saved image from Default 640x480

MOTION_TRACK_MINI_TL_ON = False     # Default= False  True= Take a mini time lapse sequence rather than a single image (overrides MOTION_VIDEO_ON)
MOTION_TRACK_MINI_TL_SEQ_SEC = 30   # Default= 30 secs Duration of complete mini timelapse sequence after initial motion detected
MOTION_TRACK_MINI_TL_TIMER_SEC = 5  # Default= 5 secs between each image. 0 is as fast as possible

MOTION_TRACK_PANTILT_SEQ_ON = False # Default= False True= Takes Pantilt Images per PANTILT_SEQ_STOPS below.

MOTION_VIDEO_ON = False      # Default= False  True=Take a video clip rather than image
MOTION_VIDEO_WIDTH = 800     # Default= 800 Width of video in pixels
MOTION_VIDEO_HEIGHT = 600    # Default= 600 Height of video in pixels
MOTION_VIDEO_FPS = 15        # Default= 15 If resolution reduced to 640x480 then slow motion is possible at 90 fps
MOTION_VIDEO_TIMER_SEC = 10  # Default= 10 secs Duration of single Video clip to take after Motion Detected
# ---------------------------------------------------------------------------

# Settings for Pan Tilt Hardware
# Pan and Tilt positions are in degrees between -90 and + 90
# ------------------------------
PANTILT_ON = False          # Default= False Off, True= Enable Pan Tilt Hat Hardware (Load Drivers)
PANTILT_IS_PIMORONI = True  # Default= True Use Pimoroni pantilehat, False= Use Waveshare pantilthat
PANTILT_HOME = (0, 0)       # Default= (0, -10) Pan Tilt Home Postion. Values between -90 and + 90
PANTILT_SLEEP_SEC = 0.1     # Default= 0.1 Allow time for pantilt servos to move

# Settings for pantilt image sequence
# Can also be triggerd by Motion if
# MOTION_TRACK_PANTILT_SEQ_ON= True
# Over Rides PANTILT_SEQ_ON=True
# otherwise PANTILT_SEQ_TIMER_SEC is Used
# ---------------------------------------
PANTILT_SEQ_ON = False      # Default= False Off, True= Enable a PanTilt Image Sequence
PANTILT_SEQ_TIMER_SEC = 300
PANTILT_SEQ_IMAGES_DIR = "media/pantilt-seq"
PANTILT_SEQ_IMAGE_PREFIX = 'pt-'
PANTILT_SEQ_RECENT_DIR = "media/recent/pt-seq"  # Default= "media/recent/pt-seq"  Location of pantilt Recent files
PANTILT_SEQ_RECENT_MAX = 40  # Default= 40 0=Off or specify number of recent files in MOTION_RECENT_DIR
PANTILT_SEQ_DAYONLY_ON = False
PANTILT_SEQ_NUM_ON = True
PANTILT_SEQ_NUM_RECYCLE_ON = True
PANTILT_SEQ_NUM_START = 1000
PANTILT_SEQ_NUM_MAX = 200
PANTILT_SEQ_STOPS = [(90, 0),
                     (45, 0),
                     (0, 0),
                     (-45, 0),
                     (-90, 0),
                    ]

# Settings for Timelapse Panoramic Image Settings
# --------------------------------------
PANO_ON = False              # Default= True Enable image stitching using pantilt overlapping images False= Disabled
                             # Note this can run in parallel with timelapse and motion tracking
                             # Image Width and Height per IMAGE_WIDTH and IMAGE_HEIGHT settings above
PANO_TIMER_SEC = 300         # Default= 300 (5 min) Duration between taking pano images (Helps avoid multiple stitch tasks)
                             # FYI Stitching time on RPI4 can be less than 10 seconds.
PANO_IMAGES_DIR = './media/pano/images'  # Dir for storing pantilt source images
PANO_DIR = './media/pano/panos'  # Dir for storing final panoramic images
PANO_IMAGE_PREFIX = 'pano-'  # Default= 'pano-' Prefix for pano images
PANO_DAYONLY_ON = True       # Default= True Take Pano only during day.  False= Day and Night
PANO_NUM_RECYCLE = True      # Default= True Recycle numbering when NUM MAX exceeded. False= Exit
PANO_NUM_START = 1000        # Default= 1000 Start of image numbering sequence
PANO_NUM_MAX   = 20          # Default= 20 Maximum number of pano's to take 0=Continuous.
PANO_PROG_PATH = '/usr/local/bin/image-stitching'  # Path to image stitching program config.cfg in pi-timolo dir.
# Set stops to take overlapping images. You need sufficient overlap for successful stitching
# Default setting [(-30, 0), (0, 0), (30, 0)] You will need to adjust for different image resolutions
# More images requires more time to stitch.  Adjust PANO_TIMER_SEC setting to avoid multiple stitches at once.
# Tested on single core RPI, but will stitch much faster on quad core.
PANO_CAM_STOPS = [(-20, 0),
                  (0, 0),
                  (20, 0)
                 ]

# Dash Cam Video Repeat Mode
# IMPORTANT: Suppresses Timelapse, Motion Track and Pano
# ------------------------------------------------------
VIDEO_REPEAT_ON = False      # Default= False OFF True= Turn on Video Repeat Mode IMPORTANT Overrides Timelapse and Motion
VIDEO_REPEAT_WIDTH = 1280    # Default= 1280 Width of video in pixels
VIDEO_REPEAT_HEIGHT = 720    # Default= 720  Height of video in pixels
VIDEO_DIR = "media/videos"   # Default= "media/videos" Storage folder path for videos
VIDEO_PREFIX = "vid-"        # Default= 'vid-" prefix for video filenames
VIDEO_START_AT = ""          # Default= "" Off or Specify date/time to Start Sequence eg "01-dec-2019 08:00:00" or "20:00:00"
VIDEO_FILE_SEC = 60          # Default= 60 seconds for each video recording
VIDEO_SESSION_MIN = 30       # Default= 30 minutes  Run Recording Session then Exit  0=Continuous
VIDEO_FPS = 15               # Default= 15 fps.  Note slow motion can be achieved at 640x480 image resolution at 90 fps
VIDEO_NUM_ON = False         # Default= False True= filenames by sequence Number  False=Filenames by date/time
VIDEO_NUM_RECYCLE_ON = False # Default= False when NumMax reached restart at NumStart instead of exiting
VIDEO_NUM_START = 1000       # Default= 1000 Start of video filename number sequence
VIDEO_NUM_MAX  = 20          # Default= 20 Max number of videos desired. 0=Continuous

# Manage Disk Space Settings
#---------------------------
SPACE_MEDIA_DIR = '/home/pi/pi-timolo2/media'  # Default= '/home/pi/pi-timolo/media'  Starting point for directory walk
SPACE_TIMER_HOURS = 0         # Default= 0  0=Off or specify hours frequency to perform free disk space check
SPACE_TARGET_MB = 500         # Default= 500  Target Free space in MB Required.
SPACE_TARGET_EXT  = 'jpg'     # Default= 'jpg' File extension to Delete Oldest Files

#======================================
#       webserver.py Settings
#======================================

# Web Server settings
# -------------------
WEB_SERVER_PORT = 8090        # Default= 8090 Web server access port eg http://192.168.1.100:8080
WEB_SERVER_ROOT = "media"     # Default= "media" webserver root path to webserver image/video su>
WEB_PAGE_TITLE = "PI-TIMOLO2" # web page title that browser show (not displayed on web page)
WEB_PAGE_REFRESH_ON = True    # False=Off (never)  Refresh True=On (per seconds below)
WEB_PAGE_REFRESH_SEC = "900"  # Default= "900" seconds to wait for web page refresh  seconds (15>
WEB_PAGE_BLANK_ON = False     # True Starts left image with a blank page until a right menu item>
                              # False displays second list[1] item since first may be in progress

# Left iFrame Image Settings
# --------------------------
WEB_IMAGE_HEIGHT = "768"       # Default= "768" px height of images to display in iframe
WEB_IFRAME_WIDTH_PERCENT = "70%" # Left Pane - Sets % of total screen width allowed for iframe. >
WEB_IFRAME_WIDTH = "100%"      # Desired frame width to display images. can be eg percent "80%" >
WEB_IFRAME_HEIGHT = "100%"     # Desired frame height to display images. Scroll bars if image la>

# Right Side Files List
# ---------------------
WEB_MAX_LIST_ENTRIES = 0           # 0 = All or Specify Max right side file entries to show (mus>
WEB_LIST_HEIGHT = WEB_IMAGE_HEIGHT # Right List - side menu height in px (link selection)
WEB_LIST_BY_DATETIME_ON = True     # True=datetime False=filename
WEB_LIST_SORT_DESC_ON = True       # reverse sort order (filename or datetime per web_list_by_da>

# ---------------------------------------------- End of User Variables -----------------------------------------------------

