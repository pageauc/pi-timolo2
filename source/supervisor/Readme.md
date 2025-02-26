## timolo2-cam.sh and timolo2-web.sh
The bash scripts manage the timolo2 supervisorctl background service for timolo2-cam.py and timolo2-web.py
per the associated [configuration .conf files ](https://raw.githubusercontent.com/pageauc/pi-timolo2/refs/heads/main/source/supervisor/timolo2-cam.conf) 
located in the supervisor folder. 
The scripts can start the .py scripts as background tasks under the specified user= in the conf file settings. 
These .conf files will by default not autostart run on boot but will attempt a restart if there is a program issue. 
Eg problem with camera.

The shell script install option creates a symlink at ***/etc/supervisor/conf.d*** folder back 
to the pi-timolo2/supervisor folder .conf files.  Use ./timolo2-cam.sh and/or timolo2-web.sh to manage options.
  
Note: Start on boot defaults to false, but can be enabled by editing the appropriate .conf file

For more details run 
    
    ./timolo2-cam.sh help
    
and/or
    
    ./timolo2-web.sh help.

example .    
./timolo2-cam.sh help

    Usage: ./timolo2-cam.sh [Option]

      Options:
      start        Start supervisor service
      stop         Stop supervisor service
      restart      restart supervisor service
      status       Status of supervisor service
      edit         nano edit /home/pi/pi-timolo2/supervisor
      log          tail -n 200 /var/log/timolo2-cam.log
      install      Install symbolic link for timolo2-cam supervisor service
      uninstall    Uninstall symbolic link for timolo2-cam supervisor service
      upgrade      Upgrade pi-timolo2 files from GitHub
      help        

    Example:  ./timolo2-cam.sh status

    Wait ...

    timolo2-cam                      RUNNING   pid 21464, uptime 3:45:51
    timolo2-web                      RUNNING   pid 21452, uptime 3:46:05
    Done

Note:

The supervisor folder .conf files default to user=pi. The .sh scripts will modify the appropriate .conf file
per the logged in user (using sed).



    