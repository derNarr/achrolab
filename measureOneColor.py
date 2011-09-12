#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./showOneColor.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)

from psychopy import visual,event,core
from ctypes import c_float

from tubes import Tubes
from monitor import Monitor
from eyeone import EyeOne
from eyeone.EyeOneConstants import TRISTIMULUS_SIZE, eNoError

eyeone = EyeOne.EyeOne()#dummy=True)
tubes = Tubes(eyeone)
mywin = visual.Window(size=(2048,1536), monitor='mymon',
                color=(0,0,0), screen=1)
mon = Monitor(eyeone, mywin)


# color170
#bg = 0.333333333333333
#voltages = (1762,2535,2277)

# color165
bg = 0.294117647059
voltages = (1607, 2310, 2182)

mon.setPatchStimColor(bg)

tri_stim = (c_float * TRISTIMULUS_SIZE)()
print("Tubes are set to correct voltages. This may take a few seconds...")
tubes.setVoltages(voltages)
print("Done.")

core.wait(0.5)

tubes.calibrateEyeOne()
tubes.startMeasurement()

if(eyeone.I1_TriggerMeasurement() != eNoError):
    print("Measurement failed for color %s ." %str(input_color))
if(eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
    print("Failed to get tri stimulus for color %s ."
            %str(input_color))
measured_color = (tri_stim[0], tri_stim[1], tri_stim[2])

print(measured_color)

mouse = event.Mouse(mywin)
show = True 

while show:
    core.wait(0.01)
    left, middle, right = mouse.getPressed()
    if left: 
        core.wait(0.2)
        show=False

