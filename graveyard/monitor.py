#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./monitor.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content: all functions for monitor stuff
#
# input: --
# output: --
#
# created 2010
# last mod 2012-05-29 14:17 DW

from eyeone.constants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    TRISTIMULUS_SIZE)
from ctypes import c_float
import time
from psychopy import visual, core


class Monitor(object):
    """
    Monitor provides an easy interface to measure psychopy.visual.PatchStim
    colors with an EyeOne Pro.
    """
    
    def __init__(self, eyeone, psychopy_win=None):
        self.eyeone = eyeone
        self.eyeone_calibrated = False
        self.psychopy_win = psychopy_win
        self.patch_stim = None

    def calibrateEyeOne(self):
        """
        Sets EyeOne Pro to correct measurement mode and calibrates EyeOne
        Pro so it is ready for use on the monitor.
        """
        # TODO: Get rid of this function, use eyeone.calibrateEyeOne
        # instead!
        print("WARNING: Everything is fine, but please change your code" + 
                " and use eyeone.calibrateEyeOne() instead of" +
                " tubes.calibrateEyeone()\n"
        self.eyeone_calibrated = self.eyeone.calibrateEyeOne()
    

    def startMeasurement(self):
        """
        Simply prompts to move EyeOne Pro to measurement position and
        waits for button response.
        """
        print("\nPlease put EyeOne Pro in measurement position for"
                + "MONITOR and press key to start measurement.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")
        


    def measurePatchStimColor(self, patch_stim_value, n=1):
        """
        Measures patch_stim_value on monitor.

        Input:
            patch_stim_value -- psychopy.visual.PatchStim color value
            n -- number of measurements (positive integer)

        
        Returns list of tuples of xyY values [(x1, y1, Y1), (x2, y2, Y2), ...]
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()
            self.startMeasurement()
        
        if not self.psychopy_win:
            self.psychopy_win = visual.Window(size=(800,600), monitor='mymon',
                    color=(0,0,0))
        if not self.patch_stim:
            self.patch_stim = visual.PatchStim(self.psychopy_win, tex=None, 
                    size=(2,2), color=patch_stim_value)
        else:
            self.patch_stim.setColor(color=patch_stim_value)
        
        xyY_list = []
        tri_stim = (c_float * TRISTIMULUS_SIZE)()

        #start measurement
        for i in range(n):
            self.patch_stim.draw()
            self.psychopy_win.flip()
            core.wait(.5)

            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed.")
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus.")
            xyY_list.append( tuple(tri_stim) )

        return xyY_list


    def measureColor(self, color, n=1):
        """
        Converts xyY color (triple of floats) to psychopy.visual.PatchStim
        color and measures color on monitor.

        Input: 
            color -- xyY color list or tuple of three floats
            n -- number of measurements (positive integer)

        Returns list of tuples of xyY values [(x1, y1, Y1), (x2, y2, Y2), ...]
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()
            self.startMeasurement()
        print("measureColor is not implemented yet.")
        # TODO measureColor
        pass
    
    def setPatchStimColor(self, patch_stim_value):
        """
        Sets monitor to patch_stim_color.
        """
        if not self.psychopy_win:
            self.psychopy_win = visual.Window(size=(2048,1536), monitor='mymon',
                    color=(0,0,0), screen=1)
        if not self.patch_stim:
            self.patch_stim = visual.PatchStim(self.psychopy_win, tex=None, 
                    size=(2,2), color=patch_stim_value)
        else:
            self.patch_stim.setColor(color=patch_stim_value)
        self.patch_stim.draw()
        self.psychopy_win.flip()



if __name__ == "__main__":
    print("1")
    from eyeone import EyeOne
    eyeone = EyeOne.EyeOne(dummy=True)
    mon = Monitor(eyeone)
    print("2")

