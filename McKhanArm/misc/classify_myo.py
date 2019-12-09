from __future__ import print_function

from collections import Counter
import struct
import sys
import time
import numpy as np
from scipy import stats
import os
from multiprocessing import Process, Pipe

# import the Grip class
sys.path.insert(1, '../misc/')
from Grip import *

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

grip_vals = ['neutral', 
			'full   ',
			'pinch  ', 
			'ball   ',
			'mug    ',
			'pencil ']

def main():
	# create an initial grip
	grip = Grip(0, 0)
	
	# most recent values
	nVals = 250
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
	if activate_display:
		# display recommended grip outputs
		print("When training the arm, here's a recommended mapping...")
		print("Value: Grip")
		print("0: Relaxed")
		print("1: All extended")
		print("2: Pinch")
		print("3: Ball")
		print("4: Mug")
		print("5: Pencil")

	try:
		while True:
			
			# note: add time dependent value updater
			# so that a value will only change iff a certain amount of time has passed
			# this would prevent he value from suddenly changing from one to another, whacking out the hand

			m.run()
			

			#********* This is the grip output **********
			r = m.history_cnt.most_common(1)[0][0] 
			#******** This is the grip certainty ********
			grip_cert = m.history_cnt[r] * 4    # makes it a value out of 100 (max is 25, ie 25*4)
			#********************************************            
			
			# view the output in the console
			#if activate_display:
				#print(f'Current grip value {int(r)}, certainty {grip_cert}%', end='\r')
				#print(f'')
			#print('Current certainty {}'.format(int(grip_cert)), end='\r')

			if HAVE_PYGAME and activate_display:
				for ev in pygame.event.get():
					if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
						raise KeyboardInterrupt()
					elif ev.type == KEYDOWN:
						if K_0 <= ev.key <= K_9:
							hnd.rline_numecording = ev.key - K_0
						elif K_KPline_num0 <= ev.key <= K_KP9:
							hnd.rline_numecording = ev.key - K_Kp0
						elif ev.uline_numnicode == 'r':
							hnd.cl.read_data()
					elif ev.type == KEYUP:
						if K_0 <= ev.key <= K_9 or K_KP0 <= ev.key <= K_KP9:
							hnd.recording = -1

				scr.fill((0, 0, 0), (0, 0, w, h))

				for i in range(10):
					x = 0
					y = 0 + 30 * i

					clr = (0,200,0) if i == r else (255,255,255)

					txt = font.render('%5d' % (m.cls.Y == i).sum(), True, (255,255,255))
					scr.blit(txt, (x + 20, y))

					txt = font.render('%d' % i, True, clr)
					scr.blit(txt, (x + 110, y))


					scr.fill((0,0,0), (x+130, y + txt.get_height() / 2 - 10, len(m.history) * 20, 20))
					scr.fill(clr, (x+130, y + txt.get_height() / 2 - 10, m.history_cnt[i] * 20, 20))

				if HAVE_SK and m.cls.nn is not None:
					dists, inds = m.cls.nn.kneighbors(hnd.emg)
					for i, (d, ind) in enumerate(zip(dists[0], inds[0])):
						y = m.cls.Y[myo.SUBSAMPLE*ind]
						text(scr, font, '%d %6d' % (y, d), (650, 20 * i))

				pygame.display.flip()
			elif activate_display:
				for i in range(10):
					if i == r: sys.stdout.write('\x1b[32m')
					print(i, '-' * m.history_cnt[i], '\x1b[K')
					if i == r: sys.stdout.write('\x1b[m')
				sys.stdout.write('\x1b[11A')
				print()

			# finding the mode should prevent bounciness
			mode_grip[gn] = r
			mode = stats.mode(mode_grip)	# get the grip that  is the mode
			mode = mode[0][0]
			percVal = mode_grip == mode		# determine the number of mode
			numGripMode = np.count_nonzero(percVal)
			#print(f"Grip: {r}, mode: {mode}, {numGripMode}")
			gn += 1

			if gn >= nVals:
				gn = 0

			if numGripMode >= 70:
				grip.val = int(mode)
				bw = int(grip.WriteSer())
				print(f'Value written={bw}, grip={grip_vals[bw]}', end='\r')	

			#if grip.val != r or grip.cert != grip_cert:
				# update the grips value

				# if numGripMode >= 66:
				# 	grip.val = r
				# 	grip.cert = grip_cert

				# basically, update the file to be a new file with a new value.
				# this is done so that there's only one line at a time.
				# I have no idea how this will preform, but it seems to me to be a little ridiculous
				# update the magical portal file between codular dimensions
				#output_data.write(str(int(r)) + ',' + str(grip_cert) + "\n")    # write the grip to a line in the text file
				



	except KeyboardInterrupt:
		pass
	finally:
		m.disconnect()
		print()

	# close the file
	output_data.close()	
	print(mode_grip)

	if HAVE_PYGAME:
		pygame.quit()

if __name__ == "__main__":
	main()
