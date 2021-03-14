# TODO:
# Add a way to convert .heic file to .jpg (apple to normal) - Might be best to do this seperately?
# Might set up a small flask page to edit the config file and start/stop/restart the script via a browser

import PiPictureFrameConfig as config
import os
import pyautogui
import subprocess
import time
import random
from PIL import Image, ImageOps

# Sets the screen to the default display
# When running manually you may need to use "DISPLAY=:0 python3 runMe.py" as well
os.environ['DISPLAY'] = ':0'


# FUNCTIONS

def print_log(message):
	# Print with the current time prepended
	# Really only needed when manually running the script to make sure it is set up correctly
	print("[{0}] {1}".format(time.strftime("%H:%M:%S"), message))

def check_start_time():
	# Checks to see if the script should sleep when started - only needed when starting manually
	# Converts everything in to minutes and then checks if we are in the sleep time window
	start_total_minutes = config.start_time_hour * 60 + config.start_time_minutes
	stop_total_minutes = config.stop_time_hour * 60 + config.stop_time_minutes
	duration_minutes = stop_total_minutes - start_total_minutes
	current_minutes = int(time.strftime("%H")) * 60 + int(time.strftime("%M"))

	# Check if the stop time is earlier timewise than the start time
	if (stop_total_minutes <= start_total_minutes):
		duration_minutes = (24 * 60 + stop_total_minutes) - start_total_minutes

	# Good to display
	if (current_minutes < start_total_minutes or current_minutes >= (start_total_minutes + duration_minutes)):
		print_log("Waiting until " + str(config.start_time_hour) + ":" + str(config.start_time_minutes) + " to start the script")
		stop_slideshow()  # Calling this will turn the screen off and sleep the script until it's ready to start
	else:
		print_log("Starting the script")

def clear_working_dir():
	# Clears the working_dir of the previous day's randomized photos
	print_log("Clearing old pictures")
	for file in os.listdir(config.working_dir):
		os.remove(os.path.join(config.working_dir, file))

def sync_gdrive():
	# Syncs the sync_dir with the Google Drive folder set in the config file
	print_log("Syncing the google drive folder with local folder")
	subprocess.call("rclone sync drive:/{0} {1}".format(config.sync_gdrive_folder, config.sync_dir), shell=True)
	print_log("Sync complete")

def resize_and_copy_pics():
	# Resizes all pictures to the width of the display, then copys them to the working_dir
	landscape_pics = []  # Holds the file names of all landscape oriented pictures, so that we don't have to go back through later

	print_log("Resizing and copying pictures to working_dir")
	for file in os.listdir(config.sync_dir):
		if (file.lower().endswith(('.png', '.jpg', '.jpeg'))):  # Only open pictures, in case other files are added to the GDrive
			image = Image.open(os.path.join(config.sync_dir, file))
		else:
			continue
		image = ImageOps.exif_transpose(image)  # Try rotating the image if it needs to be rotated (a jpg with exif orientation tag)
		w = image.size[0]
		h = image.size[1]

		# Scale the image to match the width of the screen
		scale_ratio = config.screen_width / w
		image = image.resize((int(w * scale_ratio), int(h * scale_ratio)), resample=5)

		# Check if the picture is horizontal/landscape (w > h, above the wh_ratio), add to list we return if it is
		if ((w / h) > config.wh_ratio):
			landscape_pics.append(file)

		# Save the resized image to the working_dir and close it so that we don't run out of ram
		image.save(os.path.join(config.working_dir, file))
		image.close()

	return landscape_pics

def stack_landscape_pics(landscapes):
	# Pairs up and stacks landscape pictures (w/h > 1) to reduce blank screen space when displaying pics
	random.shuffle(landscapes)  # Randomize the order we go through the landscape pics so that they get paired up differently every day

	print_log("Stacking landscape pics")
	while (len(landscapes) > 1):
		top_path = os.path.join(config.working_dir, landscapes.pop())
		bottom_path = os.path.join(config.working_dir, landscapes.pop())
		top = Image.open(top_path)
		bottom = Image.open(bottom_path)

		# Divide the difference in the height of both pictures and the screen height so that we can have
		# equal blank space at the top, bottom, and in between both pics
		spacing_height = (config.screen_height - top.size[1] - bottom.size[1]) / 3
		bottom_pic_offset = spacing_height + top.size[1] + spacing_height

		# Make a new blank image the size of the screen, then stack the two pics
		stacked = Image.new("RGB", (config.screen_width, config.screen_height))
		stacked.paste(top, (0, int(spacing_height)))
		stacked.paste(bottom, (0, int(bottom_pic_offset)))

		# Save the new image, close all 3 so we don't run out of ram, delete the non-stacked versions
		stacked.save(os.path.join(config.working_dir, "stacked_landscape_{0}.jpg".format(str(len(landscapes)))))
		stacked.close()
		top.close()
		bottom.close()
		os.remove(top_path)
		os.remove(bottom_path)
	
	if (len(landscapes) > 0):  # If we have an image left, ignore it for now and it will probably get in tomorrow
		print_log("1 landscape picture didn't get added: " + landscapes.pop())

def randomize_pics():
	# Randomizes the pictures in the working_dir so that the order they are displayed in is different every day
	file_list = os.listdir(config.working_dir)
	file_count = 0
	random.shuffle(file_list)

	print_log("Renaming randomized pics")
	for a in file_list:
		#try:
		os.rename(os.path.join(config.working_dir, a), os.path.join(config.working_dir, "pipics_{0}{1}".format(str(file_count), os.path.splitext(a)[1])))
		file_count = file_count + 1
		#except Exception as e:
		#	print ("Some error renaming the random files:" + str(e))

	file_list = os.listdir(config.working_dir)
	return file_list[0]

def start_slideshow(starting_pic):
	# Start displaying the working_dir pics using the default Raspbian/Ubuntu image viewer
	print_log("Displaying slideshow")
	subprocess.Popen(["xdg-open", os.path.join(config.working_dir, starting_pic)])
	time.sleep(5)
	pyautogui.press('f')  # One of these does full screen, can't remember what the other does
	time.sleep(1)
	pyautogui.press('f11')  # One of these does full screen, can't remember what the other does
	time.sleep(1)
	pyautogui.FAILSAFE = False  # Removes some error that was happening when moving the cursor
	pyautogui.moveTo(config.screen_height, config.screen_width)  # Move the cursor out of view (bottom right corner of the screen)
	time.sleep(1)
	subprocess.call('vcgencmd display_power 1', shell=True)  # Turn the screen on - Only needed when manually testing the script

def stop_slideshow():
	# Stops displaying pictures, turns the display off, then waits until the script needs to start again and restarts the Pi
	print_log("Stopping slideshow")
	time.sleep(3)
	pyautogui.press("esc")
	time.sleep(2)
	pyautogui.press("esc")
	time.sleep(5)
	subprocess.call("vcgencmd display_power 0", shell=True) #turn the screen off for the night (turns off the hdmi output on the Pi)

	# Calculate how many minutes until the script needs to run again, assuming that the end time is later than the start time on a 24hr clock
	minutes_until_start = (((23 - config.stop_time_hour) + config.start_time_hour) * 60) + config.start_time_minutes

	# If the end time is earlier than the start time (Ex. start at 10pm and run until 7am)
	if ((config.stop_time_hour * 60 + config.stop_time_minutes) <= (config.start_time_hour * 60 + config.start_time_minutes)):
		minutes_until_start = (config.stop_time_hour * 60 + config.stop_time_minutes) - (config.start_time_hour * 60 + config.start_time_minutes)

	# Sleep until the next day's start time, then reboot the machine
	time.sleep((minutes_until_start * 60) - config.additional_sync_time * 60) #Seconds until startTime
	os.system("reboot")  # Reboot every morning, the script will start on reboot when set up for lxsession autostart


# SCRIPT

check_start_time()
clear_working_dir()
sync_gdrive()
landscape_pics = resize_and_copy_pics()
stack_landscape_pics(landscape_pics)
first_pic = randomize_pics()
start_slideshow(first_pic)

# Cycle through the working_dir pics while we are between start_time and stop_time
# Has its limitations - won't work well if you use a very long picture time and stop just before midnight (ex. stop at 11:30 PM with 1 hour pics)
while ((int(time.strftime("%H")) * 60 + int(time.strftime('%M')) < (config.stop_time_hour * 60 + config.stop_time_minutes))): #Will run until bedTime
	time.sleep(config.pic_duration)
	pyautogui.press('right')  # Go to the next picture in GPicView

stop_slideshow()
