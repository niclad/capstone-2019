# My obj rec - object rocognition from scrath

from __future__ import print_function

import jetson.inference as ji
import jetson.utils as ju
from collections import Counter
import struct
import sys
import time
import numpy as np
from scipy import stats
import os

# import the Grip class
sys.path.insert(1, '../misc/')
import Grip

# print start-up information
print('McKAHN ARM COMBO PROGRAM')
print('To train the arm to work for you, start with classify_myo.py')
print('Press \'^C\' to stop this program')
print('Stopping for 3 seconds')
time.pause(3)

#******************************************************************************
#************************ Initialize objrec details ***************************
class Grabby:
    def __init__(self, objID, objConf):
        self.id = objID
        self.conf = objConf


# load the object detection model
net = ji.detectNet("ssd-mobilenet-v2", threshold=0.5)

# set the camera settings
camera = ju.gstCamera(1280, 720, "0")   # for mipi, use either "0" or "1"

# create an OpenGL dispaly
# Note: we don't want this, but I'm just testing stuff out rn
display = ju.glDisplay()
#********************** End objrec details ************************************
#******************************************************************************

#******************************************************************************
#**************************** Start myo details *******************************
try:
	from sklearn import neighbors, svm
	HAVE_SK = True
except ImportError:
	HAVE_SK = False

try:
	import pygame
	from pygame.locals import *
	HAVE_PYGAME = True
except ImportError:
	HAVE_PYGAME = False

from common import *
import myo

class EMGHandler(object):
	def __init__(self, m):
		self.recording = -1
		self.m = m
		self.emg = (0,) * 8

	def __call__(self, emg, moving):
		self.emg = emg
		if self.recording >= 0:
			self.m.cls.store_data(self.recording, emg)

# initialize the stuff needed for the myo:
# create an initial grip
grip = Grip(0, 0)

# most recent values
nVals = 500
mode_grip = np.zeros((nVals,), dtype=int) # a 100x1 array of 0. used to determine initial grip
# ========== Change me to make stuff display ==========
activate_display = True # change this value to surpress the visual outputs
# =====================================================
data_file = "./grip_class/classify_data.txt"
# check to see the the magic portal file exists
if os.path.isfile(data_file):
    os.remove(data_file)
    print(f"{data_file} has been removed!")

output_data = open(data_file, "w+")
print(f"{data_file} created!")

if HAVE_PYGAME and activate_display:
    pygame.init()
    w, h = 800, 320
    scr = pygame.display.set_mode((w, h))
    font = pygame.font.Font(None, 30)

m = myo.Myo(myo.NNClassifier(), sys.argv[1] if len(sys.argv) >= 2 else None)
hnd = EMGHandler(m)
m.add_emg_handler(hnd)
m.connect()
gn = 0	# gn for "grip number"

def RunMyo():			
    # note: add time dependent value updater
    # so that a value will only change iff a certain amount of time has passed
    # this would prevent he value from suddenly changing from one to another, whacking out the hand

    m.run()


    #********* This is the grip output **********
    r = m.history_cnt.most_common(1)[0][0] 
    #******** This is the grip certainty ********
    grip_cert = m.history_cnt[r] * 4    # makes it a value out of 100 (max is 25, ie 25*4)
    #********************************************            

    # finding the mode should prevent bounciness
    mode_grip[gn] = r
    mode = stats.mode(mode_grip)	# get the grip that  is the mode
    mode = mode[0][0]
    percVal = mode_grip == mode		# determine the number of mode
    numGripMode = np.count_nonzero(percVal)
    print(f"Grip: {r}, mode: {mode}, {numGripMode}")
    gn += 1

    if gn >= nVals:
        gn = 0

    if numGripMode >= 70:
        grip.val = int(mode)
        grip.cert = grip_cert
        #grip.WriteSer()

    if grip.val != r or grip.cert != grip_cert:
        # update the grips value

        # if numGripMode >= 66:
        # 	grip.val = r
        # 	grip.cert = grip_cert

        # basically, update the file to be a new file with a new value.
        # this is done so that there's only one line at a time.
        # I have no idea how this will preform, but it seems to me to be a little ridiculous
        # update the magical portal file between codular dimensions
        output_data.write(str(int(r)) + ',' + str(grip_cert) + "\n")    # write the grip to a line in the text file
    return grip
#***************************** End myo details ********************************
#******************************************************************************

def DetGrip(cam_obj, cam_conf, myo_grip, myo_cert):
    # define class IDS
    BALL = 3
    MUG = 4
    PEN = 5

    # set the recognized object to be a grip for that object
    if cam_obj == 35:
        cam_obj = PEN
    elif cam_obj == 37:
        cam_obj = BALL
    elif cam_obj == 47:
        cam_obj = MUG

    if cam_obj != myo_grip:
        if cam_obj <= myo_grip:
            return myo_grip
        else:
            # do something but what?
            return cam_obj

    if 

    





def DetectionLoop():
    thresh = 66
    # run until user exits
    while display.IsOpen():
        my_grip = RunMyo()
        
        # continue if the certainty is reasonably high 
        if my_grip.cert > thresh:
            continue

        # camera capture
        img, width, height = camera.CaptureRGBA()

        # detect objects
        detections = net.Detect(img, width, height)

        maxObj = Grabby(0,0)
        for detection in detections:
            print("The class ID is: " + str(detection.ClassID))
            print("The conf is: " + str(detection.Confidence))
            print(detection)
            
            # get the object with the highest confidence - probably a better way to determine most likely result
            if maxObj.conf < detection.Confidence:
                maxObj.id = detection.ClassID
                maxObj.conf = detection.Confidence

        display.RenderOnce(img, width, height)
        display.SetTitle("Object Detection | Network {:0} FPS".format(net.GetNetworkFPS()))

DetectionLoop()
