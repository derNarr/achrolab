#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./monitor2.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-11-25, KS

from EyeOne.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    SPECTRUM_SIZE,
                                    TRISTIMULUS_SIZE)
from ctypes import c_float
import time
from psychopy import visual, core


class Monitor(object):
    """
    Monitor provides an easy interface to measure psychopy.visual.PatchStim
    colors with an Eye One Pro.
    """
    
    def __init__(self, eye_one, psychopy_win=None):
        self.eye_one = eye_one
        self.eye_one_calibrated = False
        self.psychopy_win = psychopy_win
        self.patch_stim = None

    def calibrateEyeOne(self):
        """
        Sets the Eye One Pro to the right measurement mode and 
        calibrates the Eye One Pro for the use on the monitor.
        """
        # set EyeOne Pro variables
        if(self.eye_one.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("measurement mode set to single emission.")
        else:
            print("failed to set measurement mode.")
            return
        if(self.eye_one.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_CIExyY) ==
                eNoError):
            print("color space set to CIExyY.")
        else:
            print("failed to set color space.")
            return
        # calibrate EyeOne Pro
        print("\nPlease put the EyeOne-Pro on the calibration plate and "
        + "press the key to start calibration.")
        while(self.eye_one.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        if (self.eye_one.I1_Calibrate() == eNoError):
            print("Calibration of the EyeOne Pro done.")
        else:
            print("Calibration of the EyeOne Pro failed. Please RESTART "
            + "the calibration of the monitor.")
            return

        self.eye_one_calibrated = True
    

    def startMeasurement(self):
        """
        Simply prompt to move the Eye One Pro to measurement position and
        wait for button response.
        """
        print("\nPlease put Eye One Pro in measurement position for"
                + "MONITOR and hit the button to start measurement.")
        while(self.eye_one.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Start measurement...")
        


    def measurePatchStimColor(self, patch_stim_value, n=1):
        """
        Measures the patch_stim_value on the monitor.

        input:
            patch_stim_value -- psychopy.visual.PatchStim color value
            n -- number of measures (positive integer)

        
        returns list of tuples of xyY values
            [(x1, y1, Y1), (x2, y2, Y2), ...]
        """
        if not self.eye_one_calibrated:
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

            if(self.eye_one.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed.")
            if(self.eye_one.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus.")
            xyY_list.append( tuple(tri_stim) )

        return xyY_list


    def measureColor(self, color, n=1):
        """
        Converts colormath color to psychopy.visual.PatchStim color and
        measures the color on the monitor.

        input: 
            color -- colormath color
            n -- number of measures (positive integer)

        returns list of tuples of xyY values
            [(x1, y1, Y1), (x2, y2, Y2), ...]
        """
        if not self.eye_one_calibrated:
            self.calibrateEyeOne()
            self.startMeasurement()
        print("measureColor is not implemented yet")
        # TODO
        pass
    
    def setPatchStimColor(self, patch_stim_value):
        """
        sets the monitor to patch_stim_color.
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
    from EyeOne import EyeOne
    eye_one = EyeOne.EyeOne(dummy=True)
    mon = Monitor(eye_one)
    print("2")

