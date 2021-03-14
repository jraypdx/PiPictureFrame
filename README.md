# PiPictureFrame

A homemade picture frame with a Raspberry Pi, an LCD screen, and an HDMI driver board to connect them.

The script runs at system startup, syncs with a Google Drive folder, then turns the screen on (if it's off) and starts displaying pictures in a set time interval.  At the end of the day the screen is turned back off until it's scheduled to restart the next morning.

### Needed to use this script:

 - Rclone to sync with a Google Drive folder: https://rclone.org/drive/
 
 - A way to run the script after the Linux GUI is finished loading, ex (may vary depending on OS version): https://www.raspberrypi.org/forums/viewtopic.php?t=43509 (ex: add the line "@/usr/bin/python3 /home/pi/Documents/runMe.py" to the end of this file: "/etc/xdg/lxsession/LXDE-pi/autostart")


Note:  There is a bit of basic logging when running manually, or you can create a .sh script to call that runs the .py script with output being appended to a .txt file.
