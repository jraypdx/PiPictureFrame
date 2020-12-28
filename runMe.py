#Add a way to ignore small files? ex. less than 1mb or some dimensions
#Add a way to convert .heic file to .jpg (apple to normal) - Might be best to do this seperately?
#Add more time specifications (hours:minutes instead of just hours)
#Add config file support to make it easier to change settings without editing this script
#Add image stacking for horizontal images so that more of the screen is taken up

import pyautogui
import os
import subprocess
import time
import random
import shutil

#set screen... needed for some reason to run on boot
os.environ['DISPLAY'] = ':0'

#variables
startTime = 8 #8:00am start time for script
syncTime = 5 #Minutes to start early so there is time for pictures to sync before startTime - usually only takes a minute or so unless a lot of pictures have been added
bedTime = 22 #10:00pm end time for script
picDuration = 15 #15 seconds per picture

#turn screen off - delete later (just for demo)
#subprocess.call('vcgencmd display_power 0',shell=True)

#Clears Picture folder for randomization
for file in os.listdir('/home/pi/Pictures'):
	os.remove('/home/pi/Pictures/' + file)

#sync with our Google Drive folder
print ("Syncing the google drive folder with local folder")
subprocess.call('rclone sync drive:/Moms_digital_frame /home/pi/pics',shell=True)
print ("Sync complete")

#Get a list of the pictures)
for file in os.listdir('/home/pi/pics'):
	if ' ' in file or '(' in file or ')' in file or '\'' in file:
		print (file)
		temp = file
		temp = temp.replace(' ', '_')
		temp = temp.replace('(', 'l')
		temp = temp.replace(')', 'r')
		temp = temp.replace('\'', 'q')
		print (temp)
		os.rename("/home/pi/pics/" + file, "/home/pi/pics/" + temp)
picDir = '/home/pi/Pictures'
print ("Copying pictures")
for file in os.listdir('/home/pi/pics'):
	shutil.copy('/home/pi/pics/' + file, picDir)
picDir = '/home/pi/Pictures'
fileList = os.listdir(picDir)

#Randomize the list for displaying
print ("Randomizing pictures")
fileCount = 0
random.shuffle(fileList)
for a in fileList:
	try:
		if ".heic" in a or ".HEIC" in a:
			os.remove(picDir + "/" + a)
			print ("deleted " + a)
		else:
			os.rename(picDir + "/" + a, picDir + "/" + str(fileCount) + "." + a.split(".")[1])
			fileCount = fileCount + 1
	except:
		print ("Some error renaming the random files")
fileList = os.listdir(picDir)

#Run a slideshow through pi default image viewer
print ("Displaying slideshow")
subprocess.Popen(["xdg-open", picDir + '/' + fileList[0]])
time.sleep(5)
pyautogui.press('f')
time.sleep(1)
pyautogui.press('f11')
time.sleep(1)
#move mouse to bottom right/out of view
pyautogui.FAILSAFE = False
pyautogui.moveTo(1920,1080) #move the cursor out of view (corner of the screen)
time.sleep(1)
subprocess.call('vcgencmd display_power 1',shell=True) #turn the screen on now that we are displaying a picture
while (int(time.strftime("%H")) <= bedTime or int(time.strftime("%H")) < startTime): #Will run until bedTime
	time.sleep(picDuration)
	#print ("Next picture")
	pyautogui.press('right')
time.sleep(3)
print ("Goodnight")
pyautogui.press('esc')
time.sleep(2)
pyautogui.press('esc')
time.sleep(5)
subprocess.call('vcgencmd display_power 0',shell=True) #turn the screen off for the night (should happen approximately 10:00pm)

#dumm way to get hours until startTime that doesn't mess up if you pick midnight or early morning (ex 1am)
timeUntilStart = ((24 - bedTime) + startTime - 1) #for some reason this is one hour more than I expected so have to - 1
#while (bedTime != startTime):
#	bedTime = bedTime + 1
#	timeUntilStart = timeUntilStart + 1
#	if (bedTime == 24):
#		bedTime = 0
#subprocess.call('vcgencmd display_power 0',shell=True) #turn the screen off for the night (should happen approximately 10:00pm)

#sleep until startTime
time.sleep((timeUntilStart * 60 * 60) - syncTime * 60) #Seconds until startTime
os.system('reboot') #reboot every morning and script runs on reboot - not sure if this is a bad idea but I figured it will stop any problems from leaving it running for a long time
