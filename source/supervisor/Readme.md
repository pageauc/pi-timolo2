### supervisor folder
***timolo2.sh and webserver.sh*** use supervisorctl service to start, stop, status, Etc. timolo2.py and webserver.py per the configuration files in the supervisor folder. 
This will run the programs as background tasks under the specified user. 
These processes will not auto start on boot and will attempt a restart if there is a program issue. Eg camera issue

Note timolo2 supervisorctl configurations are stored in the pi-timolo2/supervisor folder.  The install option creates a symlink at ***/etc/supervisor/conf.d*** folder back 
to the pi-timolo2/supervisor folder.  Use timolo2.sh and/or webserver.sh edit options.  Not autostart for start on boot is disabled but can be enabled by setting to true.


For more details run ./timolo2.sh help or webserver2.sh help.