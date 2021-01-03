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
from PIL import Image
from PIL import ExifTags
from PIL import ImageOps

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
print ("clearing old pictures")
for file in os.listdir('/home/pi/Pictures'):
	os.remove('/home/pi/Pictures/' + file)

#sync with our Google Drive folder
print ("Syncing the google drive folder with local folder")
subprocess.call('rclone sync drive:/Moms_digital_frame /home/pi/pics',shell=True)
print ("Sync complete")

#Get a list of the pictures - change characters that were making issues here
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
syncedDir = '/home/pi/pics/'
print ("Copying and stacking pictures")

#for file in os.listdir('/home/pi/pics'):
#	shutil.copy('/home/pi/pics/' + file, picDir)

ratio = 1.125  # 1080/1920*2, pics at or above this ratio can be stacked and fit on the screen
landscapes = []  #holds pictures with a width to height ration greater than or equal to our needed ratio

for file in os.listdir('/home/pi/pics'):
	if (file.lower().endswith(('.png', '.jpg', '.jpeg'))):
		image = Image.open('/home/pi/pics/' + file)
	else:
		continue
	image = ImageOps.exif_transpose(image)
	w = image.size[0]
	h = image.size[1]

	#if a really small picture is added, bring it up to the minimum size of 1080 (width of the portrait 1080p screen)
	#if (w/h > 1 and w < 1080):
	scale_ratio = 1080 / w
	image = image.resize((int(w * scale_ratio), int(h * scale_ratio)), resample=5)

	try: #if image has orientation data, check it so that we don't end up with portrait pictures rotated landscape
		if (w/h >= ratio):
			landscapes.append(image)
		else: #copy portrait pictures
			image.save('/home/pi/Pictures/' + file)
			image.close()
	except Exception: #if image has no orientation data, then it is properly rotated already and we can directly check if it is landscape
		if (w/h >= ratio):
			landscapes.append(image)
		else: #copy portrait pictures
			image.save('/home/pi/Pictures/' + file)
			image.close()

random.shuffle(landscapes)
while (len(landscapes) > 1):
	image = landscapes[0]
	second = landscapes[1]  # default to the next landscape picture to stack
	for i in range(1, len(landscapes)):  # look through all and find one with a closer width, if available
		if ((image.size[0] >= second.size[0] and image.size[0] / second.size[0] <= 1.2) or ((image.size[0] <= second.size[0] and image.size[0] / second.size[0] >= .85))):
			second = landscapes[i]
			break

	landscapes.remove(image)
	landscapes.remove(second)

	#resize pics to match size (we have a lot of 4k picutres and a lot of tiny pictures apparently) - added resizing for small picture too earlier in code
	if (image.size[0] > second.size[0]):
		image = image.resize((int(image.size[0] * (second.size[0] / image.size[0])), int(image.size[1] * (second.size[0] / image.size[0]))))
	elif (second.size[0] > image.size[0]):
		second = second.resize((int(second.size[0] * (image.size[0] / second.size[0])), int(second.size[1] * (image.size[0] / second.size[0]))))

	new_width = image.size[0]
	if (second.size[0] > image.size[0]):
		new_width = second.size[0]
	new_height = new_width * 1.777 #1920/1080, the ratio of the screen in portrait
	if (image.size[1] + second.size[1] > new_height):
		new_height = image.size[1] + second.size[1]

	diff_width = abs(image.size[0] - second.size[0])
	diff_height = abs(image.size[1] - second.size[1])
	#spacing_width = (new_width - image.size[0] - second.size[0]) / 3
	spacing_height = (new_height - image.size[1] - second.size[1]) / 3

	image_x = diff_width / 2
	if (image.size[0] >= second.size[0]):
		image_x = 0
	image_y = spacing_height

	second_x = diff_width / 2
	if (second.size[0] > image.size[0]):
		second_x = 0
	second_y = (spacing_height * 2) + image.size[1]

	stacked = Image.new("RGB", (int(new_width), int(new_height)))
	stacked.paste(image, (int(image_x), int(image_y)))
	stacked.paste(second, (int(second_x), int(second_y)))
	image.close()
	second.close()
	stacked.save('/home/pi/Pictures/' + "stacked_landscape_" + str(len(landscapes)) +".jpg")
	stacked.close()

if (len(landscapes) > 0):  # if we have an image left, ignore it for now and it will probably get in next time
	print("1 landscape picture that didn't get added")

fileList = os.listdir(picDir)

#Randomize the list for displaying
print ("Randomizing pictures")
fileCount = 0
random.shuffle(fileList)
for a in fileList:
	try:
		if ".heic" in a or ".HEIC" in a or ".pdf" in a or ".mp4" in a: #remove unsupported types
			os.remove(picDir + "/" + a)
			print ("deleted " + a)
		else:
			os.rename(picDir + "/" + a, picDir + "/pipics_" + str(fileCount) + "." + a.split(".")[1])
			fileCount = fileCount + 1
	except Exception as e:
		print ("Some error renaming the random files:" + str(e))
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
