#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tubes.py
#
# (c) 2010-2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-06-28, KS
from eyeone.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    SPECTRUM_SIZE,
                                    TRISTIMULUS_SIZE)
from ctypes import c_float
import time

# only need _tub.setVoltage
import devtubes as tubes_old

from iterativeColorTubes import IterativeColorTubes

class Tubes(object):
    """
    Tubes provides an easy interface to measure a color with the Eye One
    Pro and to find for a given color the corresponding voltages.
    """

    def __init__(self, eyeone, dummy=False):
        """Initializes tubes object and stores eyeone object.

        If dummy=True no runtimelibraries will be loaded for wasco and
        EyeOne."""
        self.dummy = dummy

        self.eyeone = eyeone
        self.eyeone_calibrated = False

        self._tub = tubes_old.Tubes(self.eyeone, dummy=self.dummy)
        #self._tub.loadParameter("./calibdata/parameterTubes20110114_1506_50abs.pkl")
        self._tub.loadParameter("./calibdata/parameterTubes20110705_1533_75abs.pkl")
        #self._tub.loadParameter("./lastParameterTubes.pkl")

        self.ict = IterativeColorTubes(self, self.eyeone)

    def calibrateEyeOne(self):
        """
        Sets the Eye One Pro to the right measurement mode and 
        calibrates the Eye One Pro for the use with the tubes.
        """
        # set EyeOne Pro variables
        if(self.eyeone.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("measurement mode set to single emission.")
        else:
            print("failed to set measurement mode.")
            return
        if(self.eyeone.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_CIExyY) ==
                eNoError):
            print("color space set to CIExyY.")
        else:
            print("failed to set color space.")
            return
        # calibrate EyeOne Pro
        print("\nPlease put the EyeOne-Pro on the calibration plate and "
        + "press the key to start calibration.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        if (self.eyeone.I1_Calibrate() == eNoError):
            print("Calibration of the EyeOne Pro done.")
        else:
            print("Calibration of the EyeOne Pro failed. Please RESTART "
            + "the calibration of the monitor.")
            return

        self.eyeone_calibrated = True

    def startMeasurement(self):
        """
        Simply prompt to move the Eye One Pro to measurement position and
        wait for button response.
        """
        print("\nPlease put Eye One Pro in measurement position for TUBES"
                + " and hit the button to start measurement.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
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
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()

        xyY_list = []
        tri_stim = (c_float * TRISTIMULUS_SIZE)()

        #start measurement
        for i in range(n):
            self.setVoltages(voltages)
            time.sleep(.5)

            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed.")
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus.")
            xyY_list.append( tuple(tri_stim) )

        return xyY_list

    # returns (voltages, (x,y,Y))
    def findVoltages(self, color):
        """
        findVoltages tries to find the voltages for a given color (as
        tuple) in xyY space.
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()

        print("tubes2.findVoltages color: " + str(color))
        (voltages, xyY) = self.ict.iterativeColorMatch(
                color, epsilon=0.01, dilation=1.0, imi=0.5, max_iterations=50)
        return (voltages, xyY)

    def findVoltagesTuning(self, target_color, start_voltages=None):
        """
        findVoltagesTuning tries to aproach the voltages for a given color
        in xyY space.
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()

        print("tubes2.findVoltagesTuning color: " + str(target_color))
        return self.ict.iterativeColorMatch2(
                target_color, start_voltages=start_voltages,
                iterations=50, stepsize=10, imi=0.5)
        
    def setVoltages(self, voltages):
        """
        sets the tubes to the given voltages.
        """
        # TODO set voltages with wasco DONT use wasco, because we need to
        # smoothly change the voltages (with devtubes) -- improve devtubes
        # instead!
        self._tub.setVoltages(voltages) # old version



