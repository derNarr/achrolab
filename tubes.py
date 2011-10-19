#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./tubes.py
#
# (c) 2010-2011 Konstantin Sering <konstantin.sering [aet] gmail.com> and
# Dominik Wabersich <dominik.wabersich [aet] gmail.com>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-10-17 KS

from eyeone.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    TRISTIMULUS_SIZE)
from ctypes import c_float
import time

from math import exp,log
import numpy as np
from scipy.optimize import curve_fit

from convert import xyY2rgb

import pickle

import devtubes

from colorentry import ColorEntry

from iterativeColorTubes import IterativeColorTubes

class Tubes(object):
    """
    Gives high level access to the tubes.

    This class hides all the hardware specifications and has no
    dependencies on the eyeone module.
    """
    def __init__(self):
        """
        Initializes tubes object.

        devtub contains an object with a method setVoltages. This method
        gets a triple of integers and sets the voltages of the tubes. The
        devtubes object takes care of all the hardware stuff.
        """
        self.devtub = devtubes.DevTubes()

    def setVoltages(self, voltages):
        """
        Sets tubes to given voltages.

        If setVoltages gets an ColorEntry object, it extracts the voltages
        from this object and sets the tubes accordingly.

        WARNING: Don't set the tubes directly (e.g. via wasco), because
        the change in voltage has to be smoothly. This prevents the
        fluorescent tubes to accidentally give out.
        """
        if isinstance(voltages, ColorEntry):
            self.devtub.setVoltages(voltages.voltages)
        else:
            self.devtub.setVoltages(voltages) 


class CalibTubes(Tubes):
    """
    CalibTubes provides an easy interface to measure a color with EyeOne
    Pro and to find corresponding voltages for a given color.
    """

    def __init__(self, eyeone, calibfile="./calibdata/lastParameterTubes.pkl", dummy=False):
        """
        Initializes tubes object and stores eyeone object.

        If dummy=True no runtime libraries will be loaded for Wasco and
        EyeOne.
        """
        self.dummy = dummy

        self.eyeone = eyeone
        self.eyeone_calibrated = False
        self.IsCalibrated = False           # TODO: Why do we have 2 variables for calibrated

        self._tub = devtubes.DevTubes()
        self.loadParameter(calibfile)

        self.ict = IterativeColorTubes(self, self.eyeone)

    def calibrateEyeOne(self):
        """
        Sets EyeOne Pro to correct measurement mode and calibrates EyeOne
        Pro for use with tubes.
        """
        # set EyeOne Pro variables
        if(self.eyeone.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("Measurement mode set to single emission.")
        else:
            print("Failed to set measurement mode.")
            return
        if(self.eyeone.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_CIExyY) ==
                eNoError):
            print("Color space set to CIExyY.")
        else:
            print("Failed to set color space.")
            return
        # calibrate EyeOne Pro
        print("\nPlease put EyeOne Pro on calibration plate and "
        + "press key to start calibration.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        if (self.eyeone.I1_Calibrate() == eNoError):
            print("Calibration of EyeOne Pro done.")
        else:
            print("Calibration of EyeOne Pro failed. Please RESTART "
            + "calibration of monitor.")
            return

        self.eyeone_calibrated = True

    def startMeasurement(self):
        """
        Simply prompts to move EyeOne Pro to measurement position and
        wait for button response.
        """
        print("\nPlease put EyeOne Pro in measurement position for TUBES"
                + " and press key to start measurement.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")

    def measureVoltages(self, voltages, n=1):
        """
        Measures color of tubes for given voltages.

        Input:
            voltages -- triple of three integers (0x000, 0x000, 0x000) 
            n -- number of measurements (positive integer)
        
        Returns list of tuples of xyY values [(x1, y1, Y1), (x2, y2, Y2), ...]
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
        findVoltages tries to find voltages for a given color (as tuple) in
        xyY color space. TODO: how?
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()

        print("tubes2.findVoltages color: " + str(color))
        (voltages, xyY) = self.ict.iterativeColorMatch(
                color, epsilon=0.01, dilation=1.0, imi=0.5, max_iterations=50)
        return (voltages, xyY)

    def findVoltagesTuning(self, target_color, start_voltages=None):
        """
        findVoltagesTuning tries to find voltages for a given color
        in xyY color space.
        """
        if not self.eyeone_calibrated:
            self.calibrateEyeOne()

        print("tubes2.findVoltagesTuning color: " + str(target_color))
        return self.ict.iterativeColorMatch2(
                target_color, start_voltages=start_voltages,
                iterations=50, stepsize=10, imi=0.5)
        
    def calibrate(self, imi=0.5):
        """
        calibrate calibrates tubes with EyeOne Pro. EyeOne Pro should be
        connected to the computer. The calibration takes around 2 minutes.

            * imi -- inter measurement interval in seconds
        """
        # TODO generate logfile for every calibration

        # set EyeOne Pro variables
        if(self.eyeone.I1_SetOption(I1_MEASUREMENT_MODE, I1_SINGLE_EMISSION) ==
                eNoError):
            print("Measurement mode set to single emission.")
        else:
            print("Failed to set measurement mode.")
            return
        if(self.eyeone.I1_SetOption(COLOR_SPACE_KEY, COLOR_SPACE_RGB) ==
                eNoError):
            print("Color space set to RGB.")
        else:
            print("Failed to set color space.")
            return
        # calibrate EyeOne Pro
        print("\nPlease put EyeOne Pro on calibration plate and "
        + "press key to start calibration.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        if (self.eyeone.I1_Calibrate() == eNoError):
            print("Calibration of EyeOne Pro done.")
        else:
            print("Calibration of EyeOne Pro failed. Please RESTART"
            + " calibration of tubes.")
            return
        
        ## Measurement
        print("\nPlease put EyeOne Pro in measurement position and "
        + "press key to start measurement.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")

        # define some variables
        # generating the tested voltages (r, g, b)
        voltages = list()
        for i in range(50):
            voltages.append( ((0x400 + 61 * i), 0x0, 0x0) )
        for i in range(50):
            voltages.append( (0x0, (0x400 + 61 * i), 0x0) )
        for i in range(50):
            voltages.append( (0x0, 0x0, (0x400 + 61 * i)) )

        tri_stim = (c_float * TRISTIMULUS_SIZE)() # memory where EyeOne Pro
                                                  # saves tristim.
        rgb_list = list()
        
        for voltage in voltages:
            self.setVoltages(voltage)
            time.sleep(imi) # to give the EyeOne Pro time to adapt and to
                            # reduce carry-over effects
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for voltage %s ." %str(voltage))
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get spectrum for voltage %s ."
                        %str(voltage))
            rgb_list.append(list(tri_stim))
        
        print("Measurement finished.")
        self.setVoltages( (0x0, 0x0, 0x0) ) # to signal that the
                                            # measurement is over
        voltage_r = voltages[0]
        voltage_g = voltages[1]
        voltage_b = voltages[2]
        rgb_r = rgb_list[0]
        rgb_g = rgb_list[1]
        rgb_b = rgb_list[2]
        
        try:
            # fit a luminance function -- non-linear regression model based
            # on Pinheiro & Bates (2000)
    
            def func(x, a, b, c):
                return a + (b - a)*np.exp(-np.exp(c)*x)
            
            len3 = len(voltage_r)/3
    
            # red channel
            idr = range(len3)
            for i in idr:
                rgb_r_small = rgb_r[i]
                voltage_r_small = voltage_r[i]
            popt_r, pcov_r = curve_fit(func, voltage_r_small, rgb_r_small,
                    p0=[1000, -100, -7])
            
            # green channel
            idg = range(len3, 2*len3)
            for i in idg:
                rgb_g_small = rgb_g[i]
                voltage_g_small = voltage_g[i]
            popt_g, pcov_g = curve_fit(func, voltage_g_small, rgb_g_small,
                    p0=[1000, -100, -7])
    
            # blue channel
            idg = range(2*len3, 3*len3)
            for i in idg:
                rgb_b_small = rgb_b[i]
                voltage_b_small = voltage_b[i]
            popt_b, pcov_b = curve_fit(func, voltage_b_small, rgb_b_small,
                    p0=[1000, -100, -7])
    
            print("Parameters estimated.")
        except:
            print("Failed to estimate parameters, saved data anyway.")
            calibFile = open('calibdata/measurements/calibration_tubes' +
                    time.strftime("%Y%m%d_%H%M") +  '.txt', 'w')
            calibFile.write('voltages R:' + str(voltage_r_small) + '\n')
            calibFile.write('voltages G:' + str(voltage_g_small) + '\n')
            calibFile.write('voltages B:' + str(voltage_b_small) + '\n')
            calibFile.write('RGB R:' + str(rgb_r_small) + '\n')
            calibFile.write('RGB G:' + str(rgb_g_small) + '\n')
            calibFile.write('RGB B:' + str(rgb_b_small) + '\n')

        # save all created objects to calibration_tubes.txt
        calibFile = open('calibdata/measurements/calibration_tubes' +
                time.strftime("%Y%m%d_%H%M") +  '.txt', 'w')
        calibFile.write('voltages R:' + str(voltage_r_small) + '\n')
        calibFile.write('voltages G:' + str(voltage_g_small) + '\n')
        calibFile.write('voltages B:' + str(voltage_b_small) + '\n')
        calibFile.write('RGB R:' + str(rgb_r_small) + '\n')
        calibFile.write('RGB G:' + str(rgb_g_small) + '\n')
        calibFile.write('RGB B:' + str(rgb_b_small) + '\n')
        calibFile.write('parameters R:' + str(popt_r) + '\n')
        calibFile.write('parameters G:' + str(popt_g) + '\n')
        calibFile.write('parameters B:' + str(popt_b) + '\n')
        
        # save the estimated parameters to the tube object
        self.red_p1 = popt_r[0]
        self.red_p2 = popt_r[1]
        self.red_p3 = popt_r[2]
        self.green_p1 = popt_g[0]
        self.green_p2 = popt_g[1]
        self.green_p3 = popt_g[2]
        self.blue_p1 = popt_b[0]
        self.blue_p2 = popt_b[1]
        self.blue_p3 = popt_b[2]

        print("red_p1" + str(self.red_p1)) 
        print("red_p2" + str(self.red_p2)) 
        print("red_p3" + str(self.red_p3))
        print("green_p1" + str(self.green_p1))
        print("green_p2" + str(self.green_p2))
        print("green_p3" + str(self.green_p3))
        print("blue_p1" + str(self.blue_p1))
        print("blue_p2" + str(self.blue_p2))
        print("blue_p3" + str(self.blue_p3))
        
        # finished calibration :)
        self.IsCalibrated = True
        print("Calibration of tubes finished.")

    def setColor(self, xyY):
        """
        setColor sets the color of the tubes to given xyY values.

        * xyY is a tuple of floats (x,y,Y)
        """
        # set wasco card to correct voltage
        self.setVoltages( self.xyYtoU(xyY) )

    def xyYtoU(self, xyY):
        """
        Calculates a smart guess for corresponding voltages for a given xyY
        color (as tuple).
        """
        xyY = (xyY[0], xyY[1], xyY[2])
        rgb = xyY2rgb(xyY)
        return( (self._sRGBtoU_r(rgb[0]), 
                 self._sRGBtoU_g(rgb[1]),
                 self._sRGBtoU_b(rgb[2])) )

    def _sRGBtoU_r(self, red_sRGB):
        x = float(red_sRGB)
        if x >= self.red_p1:
            print("red channel is on maximum")
            return self.high_threshold
        U_r = (-log((x - self.red_p1)/(self.red_p2 - self.red_p1)) / 
                exp(self.red_p3))
        if U_r < self.low_threshold:
            print("red channel is on minimum")
            return self.low_threshold
        if U_r > self.high_threshold:
            print("red channel is on maximum")
            return self.high_threshold
        return int(U_r)

    def _sRGBtoU_g(self, green_sRGB):
        x = float(green_sRGB)
        if x >= self.green_p1:
            print("green channel is on maximum")
            return self.high_threshold
        U_g = (-log((x - self.green_p1)/(self.green_p2 - self.green_p1)) / 
                exp(self.green_p3))
        if U_g < self.low_threshold:
            print("green channel is on minimum")
            return self.low_threshold
        if U_g > self.high_threshold:
            print("green channel is on maximum")
            return self.high_threshold
        return int(U_g)

    def _sRGBtoU_b(self, blue_sRGB):
        x = float(blue_sRGB)
        if x >= self.blue_p1:
            print("blue channel is on maximum")
            return self.high_threshold
        U_b = (-log((x - self.blue_p1)/(self.blue_p2 - self.blue_p1)) / 
                exp(self.blue_p3))
        if U_b < self.low_threshold:
            print("blue channel is on minimum")
            return self.low_threshold
        if U_b > self.high_threshold:
            print("blue channel is on maximum")
            return self.high_threshold
        return int(U_b)


    def saveParameter(self, filename="./lastParameterTubes.pkl"):
        """
        Saves parameters used for interpolation function.
        """
        # TODO what to do, if file doesn't exist? Throw exception?
        with open(filename, 'wb') as f:
            pickle.dump(self.red_p1, f)
            pickle.dump(self.red_p2, f)
            pickle.dump(self.red_p3, f)
            pickle.dump(self.green_p1, f)
            pickle.dump(self.green_p2, f)
            pickle.dump(self.green_p3, f)
            pickle.dump(self.blue_p1, f)
            pickle.dump(self.blue_p2, f)
            pickle.dump(self.blue_p3, f)

    def loadParameter(self, filename="./lastParameterTubes.pkl"):
        """
        Loads parameters used for interpolation function.
        """
        # TODO warn if a file gets replaced?
        with open(filename, 'rb') as f: 
            self.red_p1   = pickle.load(f)
            self.red_p2   = pickle.load(f)
            self.red_p3   = pickle.load(f)
            self.green_p1 = pickle.load(f)
            self.green_p2 = pickle.load(f)
            self.green_p3 = pickle.load(f)
            self.blue_p1  = pickle.load(f)
            self.blue_p2  = pickle.load(f)
            self.blue_p3  = pickle.load(f)


    def plotCalibration(self):
        """
        plotCalibration plots luminance curves for each channel (data and
        fitted curve).
        """
        # TODO implement with matplotlib --> till then use
        # plotCalibration.R in achrolabutils
        pass

