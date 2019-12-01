# The code necessary for Anthony's microcontroller communications stuff
# written by Nicolass Tedori
# December 1, 2019

# class for Grip types
class Grip:
    '''
        A grip (for the McKhan Arm) can be any of one integers:
            1: neutral grip
            2: full extension
            3: full flexion (a fist)
            4: ball
            5: mug (like holding a mug)
            6: pinch
    '''
    def __init__(self, gripVal):
        self.val = gripVal
        self.name = None

    # set the grip name based on the grip value
    def GripName(self):
        gripName = None
        gripVal = self.val        

        if gripVal == 1:
            gripName = "neutral"
        elif gripVal == 2:
            gripName = "extension"
        elif gripVal == 3:
            gripName = "flexion"
        elif gripVal == 4:
            gripName = "ball"
        elif gripVal == 5:
            gripName = "mug"
        elif gripVal == 6:
            gripName = "pinch"
        
        self.name = gripName

    # display the current grip type
    # (as output to the console)
    def PrintGrip(self):
        print(f"Current grip: {self.name} (value: {self.val})")
            
