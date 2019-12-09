# grip control program
# Get values from the Myo classifier and the CV and determine a grip type:

# import packages/modules that may be useful
from Grip import *
import time
import classify_myo as cm
import serial
import os
from multiprocessing import Process, Queue, Pipe # this *should* allow us to run multiple loops at once
# see https://docs.python.org/3/library/multiprocessing.html for more information that is incredibly relevant

# global constants
DEFAULT_GRIP = Grip(0,100)	# the default grip for "bouncy" measurements
							# an imporvement for this would be to take the most
							# likely measurement from the bouncy grips.
							# this is less time consuming though

# open the data in the grip_class directory
def ReadData(file_name):
	data_dir = "./grip_class/"
	file_dir = data_dir + file_name
	filehandle = open(file_dir, "r")
	return filehandle

if __name__ == "__main__":
	print(f'Running McKahn Arm Grip Determiner 3000!')

	# run the scripts from this script
	# -- I'm thinking this will start the script as if we had in a seperate terminal window
	#    but just from this python script... but lets see?
	# runs in the same terminal, so the output from this file is impossible to see
	#os.system('python3 classify_myo.py')

	# grip pipe
	parent_conn, child_conn = Pipe()
	p = Process(target=cm.main, args=())
	p.start()

	while True:
		grip = parent_conn.recv()


		# open the data files
		myo_grip = ReadData("classify_data.txt")
		grip_prev = 0
		cert_prev = 0

		# read the last line of the file -- THIS DOES NOT WORK
		# myo_list = myo_grip.readlines()		# read the lines from the file
		# myo_grip.close()					# close the file (opening again next time)
		# myo_last = myo_list[-1]				# get the last line (aka the most recent value)
		# myo_last = myo_last.split(',')		# split the line by the delimiter ","
		# grip_curr = myo_last[0]				# get the grip id
		# cert_curr = myo_last[1]				# get the grip certainty

		# print the grip and certainty with a carriage return
		print(f'Grip: class {grip.val}, certainty {grip.cert}', end='\r')
rint ("THIS IS A TEST OF PYTHON") # this prints
