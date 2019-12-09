# test serial output in python

import serial

# create the serial port (according to what *I* know)
port = '/dev/ttyACM0'   # serial port
br = int(9600)          # baudrate (not sure what this number should actually be)
ser = serial.Serial(port, br)     # open the the serial port correstponding to a USB

# open the serial port
if not ser.is_open:
    ser.open()

for i in range(10):
    bw = ser.write(i)       # bytwes written -- likely to be 1 (if something is written)
    print('i=' + str(i))    # print the value of i
    print('bw=' + str(bw))  # print the number of bytes returned
    # getting values for bw so i assume this is working?

# close the serial port
ser.close()

