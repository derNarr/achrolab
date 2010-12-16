#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tubes2.py
#
# (c) 2010 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2010-12-09, KS
from colormath.color_objects import xyYColor
from EyeOne.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    SPECTRUM_SIZE,
                                    TRISTIMULUS_SIZE)
from ctypes import c_float
import time

# only need _tub.setVoltage
import tubes as tubes_old
_tub = tubes_old.Tubes()
_tub.loadParameter("./data/parameterTubes20101209_1136.pkl")

import iterativeColorTubes

class Tubes(object):
    """
    Tubes provides an easy interface to measure a color with the Eye One
    Pro and to find for a given color the corresponding voltages.
    """

    def __init__(self, eye_one):
        self.eye_one = eye_one
        self.eye_one_calibrated = False

    def calibrateEyeOne(self):
        """
        Sets the Eye One Pro to the right measurement mode and 
        calibrates the Eye One Pro for the use with the tubes.
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
        print("\nPlease put Eye One Pro in measurement position for TUBES"
                + " and hit the button to start measurement.")
        while(self.eye_one.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Start measurement...")

    def measureVoltages(self, voltages, n=1):
        """
        Measures the color of the tubes for given voltages.

        input:
            voltages -- triple of three integers (0x000, 0x000, 0x000) 
            n -- number of measures (positive integer)
        
        returns list of tuples of xyY values
            [(x1, y1, Y1), (x2, y2, Y2), ...]
        """
        if not self.eye_one_calibrated:
            self.calibrateEyeOne()

        xyY_list = []
        tri_stim = (c_float * TRISTIMULUS_SIZE)()

        #start measurement
        for i in range(n):
            self.setVoltages(voltages)
            time.sleep(.5)

            if(self.eye_one.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed.")
            if(self.eye_one.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus.")
            xyY_list.append( tuple(tri_stim) )

        return xyY_list

    def findVoltages(self, color):
        """
        findVoltages tries to find the voltages for a given color in xyY
        space.
        """
        if not self.eye_one_calibrated:
            self.calibrateEyeOne()

        #(voltages, xyY) = iterativeColorTubes.iterativeColormatch(
        #        color, self.eye_one, _tub,
        #        epsilon=0.01, streckung=1.0, imi=0.5, max_iterations=50)
        if isinstance(color, tuple):
            color = xyYColor(color[0], color[1], color[2])
            color = color.convert_to('rgb', target_rgb='sRGB', clip=False)
        print("tubes2.findVoltages color: " + str(color))
        (voltages, rgb) = iterativeColorTubes.iterativeColormatchRGB(
                color, self.eye_one, _tub,
                epsilon=3.0, streckung=0.9, imi=0.5, max_iterations=50)
        if rgb:
            xyY = rgb.convert_to('xyY')
        else:
            xyY = None

        return (voltages, xyY)

    def findVoltagesTuning(self, color, start_voltages=None):
        """
        findVoltagesTuning tries to aproach the voltages for a given color
        in xyY space.
        """
        if not self.eye_one_calibrated:
            self.calibrateEyeOne()

        if isinstance(color, tuple):
            color = xyYColor(color[0], color[1], color[2])
            color = color.convert_to('rgb', target_rgb='sRGB', clip=False)
        print("tubes2.findVoltagesTuning color: " + str(color))
        return iterativeColorTubes.iterativeColormatch2(
                color, self.eye_one, _tub, start_voltages=start_voltages,
                iterations=5, stepsize=10, imi=0.5)
        
    def setVoltages(self, voltages):
        """
        sets the tubes to the given voltages.
        """
        # TODO set voltages with wasco
        _tub.setVoltage(voltages) # old version



