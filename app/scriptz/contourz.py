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

import cv2


## -------------------------------------------------------
## Config
## -------------------------------------------------------

## set global for image being manipulated to keep the file persistant?
geometricImagePath = os.path.join(os.path.dirname(__file__), '..', 'static\images\geometric')
userImagePath = os.path.join(os.path.dirname(__file__), '..', 'static\images\user')


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
			
			# Reset list for each image
			geometricImageDetail = []

			# Build file path
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

Get user supplied images

"""
def userImage():

	global userImagePath
	global userImageCount

	# Get list of images in directory
	dirList = os.listdir(userImagePath)
	
	# Build file path
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



def returnContourz():

	processGeometricImages()

	global geometricImageData

	return geometricImageData



def returnImagz(cnt):

	# Get first two images
	# First image to use
	imNow = loadUserImage()
	# Second image to transition to
	imNext = loadUserImage()

	#cnt = getNextContour()

	mask = np.zeros(imNow.shape, np.uint8)

	cv2.drawContours(mask, [cnt], 0, 255, -1) 

	return imageTransition(mask, imNext, imNow)