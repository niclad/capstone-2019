# The code necessary for Anthony's microcontroller communications stuff
# written by Nicolass Tedori
# December 1, 2019

import serial

# class for Grip types
class Grip:
    '''
        A grip (for the McKhan Arm) can be any of one integers:
            0: neutral grip
            1: full extension
            2: pinch
            3: ball
            4: mug (like holding a mug)
            5: pencil
    '''
    def __init__(self, gripVal, gripCert):
        self.val = gripVal
        self.cert = gripCert
        self.name = None
        self.ser = serial.Serial("/dev/ttyACM0", int(9600))

    def __del__(self):
        self.ser.close()

    # set the grip name based on the grip value
    def GripName(self):
        gripName = None
        gripVal = self.val        

        if gripVal == 0:
            gripName = "neutral"
        elif gripVal == 1:
            gripName = "extension"
        elif gripVal == 2:
            gripName = "pinch"
        elif gripVal == 3:
            gripName = "ball"
        elif gripVal == 4:
            gripName = "mug"
        elif gripVal == 5:
            gripName = "pencil"
        
        self.name = gripName

    # display the current grip type
    # (as output to the console)
    def PrintGrip(self):
        print(f"Current grip: {self.name} (value: {self.val})")

    # write a value to the serial portand return the value written
    def WriteSer(self):
        return self.ser.write(self.val)
            
