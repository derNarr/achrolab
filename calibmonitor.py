#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./calibmonitor.py
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
# last mod 2012-06-14 16:45 KS

"""
This module provides the calls CalibMonitor which handles measuring of the
monitor.
"""

from eyeone.constants import eNoError, TRISTIMULUS_SIZE
from ctypes import c_float
import time
from monitor import Monitor


class CalibMonitor(Monitor):
    """
    provides an easy interface to measure psychopy.visual.PatchStim
    colors with an EyeOne Pro.
    """
    
    def __init__(self, eyeone, psychopy_win=None):
        Monitor.__init__(self, psychopy_win)
        self.eyeone = eyeone
        self.eyeone_calibrated = False

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
        if not self.eyeone.is_calibrated:
            self.eyeone.calibrate()
            self.startMeasurement()

        self.setColor(patch_stim_value)
        xyY_list = []
        tri_stim = (c_float * TRISTIMULUS_SIZE)()

        #start measurement
        for i in range(n):
            self.patch_stim.draw()
            self.psychopy_win.flip()
            time.sleep(.5)

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
        if not self.eyeone.is_calibrated:
            self.eyeone.calibrate()
            self.startMeasurement()
        print("measureColor is not implemented yet.")
        # TODO measureColor
        pass


if __name__ == "__main__":
    print("1")
    from eyeone import eyeone
    eyeone = eyeone.EyeOne(dummy=True)
    mon = CalibMonitor(eyeone)
    print("2")

