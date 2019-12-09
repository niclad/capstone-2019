from __future__ import print_function

from collections import Counter
import struct
import sys
import time

import numpy as np
from scipy import stats
import serial

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

if __name__ == '__main__':

    # list of grips
    grip_vals = ['neutral  ', 
			     'full     ',
			     'pinch    ', 
			     'extension']

    if HAVE_PYGAME:
        pygame.init()
        w, h = 800, 320
        scr = pygame.display.set_mode((w, h))
        font = pygame.font.Font(None, 30)

    m = myo.Myo(myo.NNClassifier(), sys.argv[1] if len(sys.argv) >= 2 else None)
    hnd = EMGHandler(m)
    m.add_emg_handler(hnd)
    m.connect()
    #ser = serial.Serial('/dev/ttyACM0', int(9600)) # could be same port as myoband, so perhaps im screwing it up?
    N_VALS = 250
    prev_grips = np.zeros((100,), dtype=int)
    gnum = 0
    try:
        while True:
            m.run()

            # get the current grip value and add it to the list
            r = m.history_cnt.most_common(1)[0][0]
            prev_grips[gnum] = r
            
            if gnum % 10 == 0:
                grip_modal_stats = stats.mode(prev_grips)    # get the mode of the grips
                grip_mode = grip_modal_stats[0][0]              # get the actual modal value from mode()
                num_mode = grip_modal_stats[1][0]               # get the number of values that equal the mode

            # if the mode reaches a relatively high frequency, send that value
            if num_mode >= 70:
                bw = grip_mode      # send via serial (in a perfect world)
                print(f"Value sent={bw}, grip={grip_vals[grip_mode]}", end="\r")    # print the grip and sent value

            # update the index value
            gnum += 1
            if gnum > 99:
                gnum = 0    # reset the index value if it's !w/in grip_vals range

            if HAVE_PYGAME:
                for ev in pygame.event.get():
                    if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                        raise KeyboardInterrupt()
                    elif ev.type == KEYDOWN:
                        if K_0 <= ev.key <= K_9:
                            hnd.recording = ev.key - K_0
                        elif K_KP0 <= ev.key <= K_KP9:
                            hnd.recording = ev.key - K_Kp0
                        elif ev.unicode == 'r':
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
            else:
                for i in range(10):
                    if i == r: sys.stdout.write('\x1b[32m')
                    print(i, '-' * m.history_cnt[i], '\x1b[K')
                    if i == r: sys.stdout.write('\x1b[m')
                sys.stdout.write('\x1b[11A')
                print()

    except KeyboardInterrupt:
        pass
    finally:
        m.disconnect()
        print()

    if HAVE_PYGAME:
        pygame.quit()
