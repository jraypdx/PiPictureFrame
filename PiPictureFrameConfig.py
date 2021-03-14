# Config file for the PiPictureFrame runMe.py script
# Keep this in the same directory as the runMe.py script

# What time (hour) to start the script at (ex. 8 = 8 AM in the morning)
start_time_hour = 8

# What time (minutes in the range 0-59) to start the script at
# (ex. startTimeHour = 8 and startTimeMinutes = 30, the script will start at 8:30 AM)
start_time_minutes = 0

# Minutes needed for syncing and setup - the screen will show the default Raspbian/Ubuntu desktop while syncing and preparing
additional_sync_time = 5

# What time (hour) to stop displaying pictures and turn the screen off (ex. 22 = 10 PM at night)
stop_time_hour = 22

# What time (minutes in the range 0-59) to stop the script and turn the screen off
# (ex. bedTimeHour = 22 and bedTimeMinutes = 30, the script will stop at 10:30 PM)
stop_time_minutes = 0

# How many seconds to display each picture
pic_duration = 15

# Name of the Google Drive folder to sync to
sync_gdrive_folder = "Moms_digital_frame"

# Directory that holds untouched pictures to use, in my case the one that is synced with Google Drive
sync_dir = '/home/pi/pics/'

# Directory that is used for copying pictures to, resizing them, stacking them, randomizing them, and then displaying them
working_dir = '/home/pi/Pictures/'

# Width of the display screen - pictures will be resized to fit this width (ex. 1080 for a vertical 1920x1080 screen)
screen_width = 1080

# Height of the display screen - used to move the mouse cursor out of the way
screen_height = 1920

# Pictures with a width to height ratio at or greater than this will be considered horizontal/landscape
# and will be stacked with another horizontal/landscape photo (this is for a vertical/portrait display screen)
wh_ratio = 1.125


