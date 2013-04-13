# DEBUGGING
# if you need to debug your code put this line in where every you want a break point:
# import ipdb; ipdb.set_trace()
# you will most likely have to pip install ipdb to use it

from datetime import datetime

from math import fabs 
import random
#from main_functions import sample

import os # access to file directory
import numpy as np

import pyaudio
import analyse

import cv2


## -------------------------------------------------------
## Config
## -------------------------------------------------------

## set global for image being manipulated to keep the file persistant?
geometricImagePath = os.path.join(os.path.dirname(__file__), '..', 'static\images\geometric')
userImagePath = os.path.join(os.path.dirname(__file__), '..', 'static\images\user')


## set which image to use within user image list
userImageCount = 0


freqThreshold = 0
colorTempOptions = [ 'warm', 'cool' ]


currentGeometricImage = 0
currentGeometricImageContour = 0


# set lists for geometric image detail
geometricImageData = []
#geometricImageList = []
geometricImageDetail = []


## set image size used in resizing user images
width = 0
height = 0


## -------------------------------------------------------
## Geometric images
## -------------------------------------------------------

## Get geometric images from directory and immediately threshold/contour all of them in a loop

## Once this is initially run, can the results be saved in a text file or some other saved format 
## accessible each time the application is run rather than having to process them each time?

"""

Process all geometric images and save in geometricImageData list for future reference

"""
def processGeometricImages():
	
	i = 1

	# Used to reference geometric image contours application wide
	global geometricImageData

	# Get list of images in directory
	dirList = os.listdir(geometricImagePath)

	for fileName in dirList:
		
		if not fileName.startswith('.') and not fileName.startswith('Thumbs'):
			
			#print fileName
			# Reset list for each image
			geometricImageDetail = []

			# Build file path
			#finalFilePath = geometricImagePath
			#finalFilePath += "\\"
			#finalFilePath += fileName
			finalFilePath = os.path.join(os.path.dirname(__file__), '..', 'static\images\geometric', fileName)

			# Get image
			im = cv2.imread(finalFilePath) 

			# Convert image to grayscale
			imGray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
			
			# Set image size used in resizing user images
			global width
			global height
			width, height = imGray.shape

			# Threshold image
			ret, thresh = cv2.threshold(imGray, 254, 255, 0) 

	##
	## TO-DO: 
	## Dilate thresh with small structuring element and 
	## Erode to makeup for stroke width of geometric image
	##

			# Get contours
			contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


			# Create image masks
			for h, cnt in enumerate(contours): # Enumerate will return both the key and value from the list item

				# Reject small areas
				if len(cnt) > 20:
					
					geometricImageDetail.append(cnt)

					mask = np.zeros(imGray.shape, np.uint8)

					cv2.drawContours(mask, [cnt], 0, 255, -1)


			geometricImageData.append(geometricImageDetail)

			i += 1


"""

Wrapper for geometricImage(i)

"""
def loadGeometricImage(i):

	return geometricImage(i)


"""

Return geometric image

"""
def geometricImage(i):

	global geometricImageData

	# Set image range
	geometricImageListLength = len(geometricImageData)

	# Is image being requested within the range of image available?
	if i <= geometricImageListLength:
		return geometricImageData[i]
	# Default to the first image if out of range
	else:
		return geometricImageData[0] #userImage = cv2.imread(dirList[(userImageCount - dirListLen)])


""" 

Return next contour within current geometric image

"""
def getNextContour():

	global currentGeometricImage
	global currentGeometricImageContour

	# Set contour range
	contourLength = len(geometricImageData[currentGeometricImage]) - 1 # subtract 1 to account for 0 based keys

	# Is contour being requested within the range of contours available?
	if currentGeometricImageContour <= contourLength:
		nextContour = geometricImageData[currentGeometricImage][currentGeometricImageContour]
	# Default to the first contour if out of range
	else:
		currentGeometricImageContour = 0
		nextContour = geometricImageData[currentGeometricImage][currentGeometricImageContour]
	
	currentGeometricImageContour += 1

	return nextContour


### production -------------------------------------------------------


## -------------------------------------------------------
## user submitted images
## -------------------------------------------------------

"""

Wrapper for userImage()

Keep track of image in use with userImageCount

"""
def loadUserImage():

	userImageData = userImage()
	
	global userImageCount
	userImageCount += 1

	return userImageData


"""

Get user supplied image

"""
def userImage():

	global userImagePath
	global userImageCount

	# Get list of images in directory
	dirList = os.listdir(userImagePath)
	
	# Build file path
	#filePath = userImagePath
	#filePath += "/"
	filePath = os.path.join(os.path.dirname(__file__), '..', 'static\images\user')

	# Set image range
	dirListLen = len(dirList) - 1 # subtract 1 to account for 0 based keys

## 
## TO-DO - better way to construct this conditional set to share with getNextContour() ?
##
	# If number of items in dirList is out of range of userImageCount, load image within range instead
	if userImageCount <= dirListLen:
		filePath += dirList[userImageCount]
	# Default to the first image if out of range
	else:
		userImageCount = 0
		filePath += dirList[userImageCount]


	# Get image
	im = cv2.imread(filePath)

	# Resize image to match dimensions of geometric images
	im = resizeUserImage(im)

	return im


"""

Resize image to match dimensions of geometric images

"""
def resizeUserImage(im):

	global width
	global height

	return cv2.resize(im, (width,height))


## -------------------------------------------------------
## image transitions
## -------------------------------------------------------


## 
## TO-DO - Is this still needed ?
##
def geometricTransition():

	## get geometric image based on frequency range, and/or tempo --- more? ______
		## should all geometric images have one area in common to make smooth transitions, such as a circle in the middle? 
		## **Or is one transition just a more complicated version of the previous from 1-20, or takes the previous and adds to it?

	return 1


"""

Set image transitions

Uses contour mask area from processGeometricImages() to determine where the images are combined

"""
def imageTransition(mask, image, imageNext):

	## take next portion of imNext and place it over imNow

	## set count of geometric contours in currently selected image and subtract by number already used

	## define when to call next (3rd, 4th, etc.) image
		## if count of contours already used is within 75% to total contours, load next image ?
			## how long will it take to load an image ? Milliseconds?

	
	mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

	#mask = cv2.bitwise_not(mask,mask)
	#mask = cv2.GaussianBlur(mask,(3,3),0)

	image = cv2.bitwise_not(image,image)

	image = cv2.bitwise_not(image,imageNext,mask)

	return image


## -------------------------------------------------------
## color transitions
## -------------------------------------------------------

"""

Set color transitions

Uses contour mask area from processGeometricImages() to determine where the color change takes place

"""
def colorTransition(mask, color, image):

	colorOverlay = mask #cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

	colorOverlay[np.where((colorOverlay == [255,255,255]).all(axis = 2))] = color #[255,0,0]

##
## TO-DO: Use cvInRangeS() and cvAnd() to replace colors in image?
##
	image = cv2.bitwise_xor(image,colorOverlay) #image = cv2.bitwise_and(image,colorOverlay)

	return image


## -------------------------------------------------------
## colors
## -------------------------------------------------------


def setColorTemperature(freq): 

	## determine color temperature
	colorTemp = 'cool'
	
	global freqThreshold
	
	if(freq > freqThreshold): 
		# set warm color
		colorTemp = 'warm'
	
	return colorTemp


def setColor(colorTemp): 

	if(colorTemp == 'warm'): 
		# generate warm color
		# red - 255,0,0
		# orange - 255,165,0
		# yellow - 255,255,0
		## can this format be rgb, or does it need to be bgr?
		color = [ random.randint(205,255), random.randint(0,255), 0 ]

	else:
		# generate cool color
		# blue - 0,0,255
		# green - 0,128,0  or  lime - 0,255,0 
		# purple - 128,0,128  or  magenta - 255,0,255
		## can this format be rgb, or does it need to be bgr?
		color = [ 0, random.randint(0,255), random.randint(0,255) ]

	return color



### audio -------------------------------------------------------


def sample():

    chunk = 1024
    
    FORMAT = pyaudio.paInt16
    
    CHANNELS = 1 
    
    # Specifies the desired sampling rate (in Hz)
    # 44100 is the sampling rate used in cds - http://en.wikipedia.org/wiki/44,100_Hz
    RATE = 44100


    metrics = []

    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = chunk)

    data = stream.read(chunk)
    samps = np.fromstring(data, dtype = np.int16)

    # Get decibels
    dbs = analyse.loudness(samps)

    # Get pitch
    pitches = analyse.musical_detect_pitch(samps)

    stream.close()
    p.terminate()

    # Get frequency in Hertz
    fftData = abs(np.fft.rfft(samps))**2
    which = fftData[1:].argmax() + 1

    if which != len(fftData)-1:
            y0, y1, y2 = np.log(fftData[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
            thefreq = (which+x1)*RATE / chunk
    else:
        thefreq = which*RATE/chunk

    metrics.append(thefreq)
    metrics.append(dbs)
    metrics.append(pitches)

    return metrics


def setFreqThreshold(): 

	global freqThreshold

##
## TO-DO
## replace 2000 with real number to use - number should be determined dynamically? 
## or default to average mean frequency for music, guitar, vocals, etc?
##
	freqThreshold = 2000;

	return freqThreshold


## take frequency range in first 4 seconds as norm ? 
## how to define first time period ? 
	# when more than one pitch is encountered ?
	# when loudness increases and stays consistent for 1-2 seconds?

## evaluate frequency
	# what is the standard range?
# If the frequencies in the audio data window include a large range, 
# the application will use a geometric composition with a large number of shapes. 
# An audio data window with a short frequency range will use less complex geometric compositions. 

## evaluate pitch
	# how many pitches should we expect to encounter in a piece of music ?
	# how many frequencies does each pitch encompass?
# significant change calls ________ function - same as frequency above?

## evaluate tempo
	# how much change in tempo is typical versus significant?
# significant change calls imageTransition() ?
# significant change calls geometricTransition() ? The faster the tempo the more complex the geometric image ?

## evaluate decibels / loudness
	# what is the standard range?
# Alternative if tempo determination is not accurate:
	# The rate in which the imagery changes will be determined by the decibels of the audio. 
	# High decibels will create faster image changes, while lower decibels will create more gradual image changes.

## how to determine when the music is changing (for example - moving from verse to chorus) ?
## when to set a new norm to base decisions off ?
	# look for significant changes that stay consistent for 4 seconds?
		# use pitch for traditional pop songs ?



### main file -------------------------------------------------------

def returnContourz():
	# cv2.namedWindow( "Display window" )

	processGeometricImages()

	global geometricImageData

	return geometricImageData
	#return getNextContour()




	# initialize list
	audioMetricsList = []
	audioWindow = []


	## -------------------------------------------------------
	## user submitted images
	## -------------------------------------------------------

	# Get first two images
	# First image to use
	imNow = loadUserImage()
	# Second image to transition to
	imNext = loadUserImage()

	# Minimum window used in evaluating audio metric samples
	# 10 samples will run ~0.6 seconds on this computer, which translates to ~100bpm (1 beat per 0.6 seconds)
	minimumWindow = 10 

	i = 1 # TO-DO: needed after testing?

	#print datetime.now() # TO-DO: delete after testing

	# 
	# TO-DO ?
	# Run a test in while loop below to check speed of loop
	# This will determine how many iterations are run per second
	# The number of iterations per second (or .5 sec, .3 sec, etc) could be the minimumWindow length?
	#
	# Determine bpm by comparing iterations per second and number of pitch changes or decibel peaks?
	#
	while(i <= 100): # TO-DO: needed after testing?

		# Process audio sample a minimum of once per second
		audioMetrics = sample() # sample() returns a list of [frequency, loudness, pitch]

		audioMetricsList.append(audioMetrics)


		### begin image manipulation

		
		### window audioMetrics into groups of x ? Start with current and get last x-1 windows?
		audioWindow = audioMetricsList[-minimumWindow:] # this should not throw an error if list contains less than x items

	# Testing freq evaluation
		totalSample = 0

		for data in audioWindow:
			totalSample += data[0]

		if audioMetrics[0] > (totalSample/(minimumWindow - 1)):
			print i

	#	
	# TO-DO - start analyzing groups that came before audioWindow
	# compare audioWindow to audioMetricsList[-minimumWindow*8:-minimumWindow] (current window to previous ~32)?
	#

		# Set threshold for audio frequency
		freqThreshold = setFreqThreshold() #audioWindow

		
		# Define frequency complexity. This will determine which geometric composition is used.
		### possible for freqComplexity to remain between 1-20?
#		freqComplexity = int(round(fabs(freqThreshold / audioMetrics[0]))) # fabs imported from math


		# set geometric image - only after first two windows have been created?
		#loadGeometricImage(freqComplexity)


	##
	## TO-DO:
	## HOW TO KNOW WHEN TO CHANGE COLOR - need significant diff from threshold?
	##
		# warm or cold color temp based on frequency
		colorTemp = setColorTemperature(audioMetrics[0])
		color = setColor(colorTemp)
		#print color


		# Trigger image manipulation based on audio frequency
		freqTrigger = 0
		freqTrigger = audioMetrics[0] > freqThreshold


		# Trigger image manipulation based on audio decibel level
		decibelTrigger = 0
		decibelTrigger = audioMetrics[1] > -10


		if freqTrigger or decibelTrigger:

			# Get next geometric contour
			cnt = getNextContour()

			mask = np.zeros(imNow.shape, np.uint8)

			cv2.drawContours(mask, [cnt], 0, 255, -1) 

			if decibelTrigger:
				# The rate in which the imagery changes will be determined by the decibels of the audio. 
				# High decibels will create faster image changes, while lower decibels will create more gradual image changes. 
				# Decibel range will be determined by comparing the current decibel value to past decibel values collected by the application.
				imNow = imageTransition(mask, imNext, imNow)

			else:
				# Color manipulation will be chosen based on audio frequencies. 
				# Low frequencies will generate cool colors, while high frequencies will generate warm colors. 
				imNow = colorTransition(mask, color, imNow) #cv2.bitwise_xor(imNow,colorOverlay)

	# Testing - show image in window
			#cv2.imshow("Display window", imNow); #showImage("Display window", imNow) 
			#cv2.waitKey(0);
			#cv2.imshow("Display window", imNext);
			#cv2.waitKey(0);

		i += 1

	#print datetime.now() # TO-DO: delete after testing

	cv2.waitKey(0);


	### GENERAL STUFF STILL NEEDED

	### 
	### When to restart/reset all variables and begin new song? 
	###	# Find when freq range is ~0 for 2+ windows?
	###