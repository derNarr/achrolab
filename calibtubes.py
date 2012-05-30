#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# calibtubes.py
#
# (c) 2010-2012 Konstantin Sering, Nora Umbach, Dominik Wabersich
# <colorlab[at]psycho.uni-tuebingen.de>
#
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# content:
#
# input: --
# output: --
#
# created 2012-05-29 KS
# last mod 2012-05-30 12:40 KS

"""
This modules provides CalibTubes.
"""

from ctypes import c_float
import time
from exceptions import ValueError

from math import exp, log
from scipy.optimize import curve_fit

import pickle

from tubes import Tubes
from eyeone.constants import TRISTIMULUS_SIZE, SPECTRUM_SIZE, eNoError


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
        self.is_calibrated = False
        self.loadParameter(calibfile)

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

    def measureVoltages(self, voltages, imi=0.5, each=1):
        """
        Measures color of tubes for given voltages.

        :Parameters:

            voltages : ( (vol_r1, vol_g1, volb1), (vol_r2, vol_g2, vol_b2), ...)
                a list of triples of integers
            imi : *0.5* or any positive float
                inter measurement interval in seconds
            each : *1* or any positive integer
                number of measurements per voltage

        Returns list of tripels (voltages, yxY, spectrum). All elements of
        the triples are tuples as well. For example: [( (vol_r1, vol_g1,
        vol_b1), (x1, y1, Y1), (l_1, l_2, l_3, ..., l_36) ), ...]

        """
        self.printNote()
        if not self.eyeone.is_calibrated:
            self.eyeone.calibrate()

        vol_col_spec_list = list()
        tri_stim = (c_float * TRISTIMULUS_SIZE)() # memory where EyeOne Pro
                                                  # saves tristim.
        spectrum = (c_float * SPECTRUM_SIZE)()    # memory where EyeOne Pro
                                                  # saves spectrum.
        #start measurement
        filename = ('calibdata/measurements/measure_tubes_' +
                    time.strftime("%Y%m%d_%H%M") + '.txt')
        print("writing measurements in " + filename)
        with open(filename, 'w') as calibfile:
            calibfile.write("volR, volG, volB, x, y, Y," +
                    ", ".join(["l" + str(x) for x in range(1,37)]) + "\n")
            print("Starting measurement...")
            for voltage in voltages:
                for i in range(each):
                    self.setVoltages(voltage)
                    print(voltage)
                    time.sleep(imi) # to give the EyeOne Pro time to adapt
                                    # and to reduce carry-over effects
                    if(eyeone.I1_TriggerMeasurement() != eNoError):
                        print("Measurement failed for voltage %s ."
                                %str(voltage))
                    if(eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                        print("Failed to get tristim for voltage %s ."
                                %str(voltage))
                    if(eyeone.I1_GetSpectrum(spectrum, 0) != eNoError):
                        print("Failed to get spectrum for voltage %s ."
                                %str(voltage))
                    #write data #TODO output.py
                    calibfile.write(", ".join([str(x) for x in voltage]) +
                            ", " + ", ".join([str(x) for x in tri_stim]) +
                            ", " + ", ".join([str(x) for x in spectrum]) +
                            "\n")
                    calibfile.flush()
                    #store data in lists
                    vol_col_spec_list.append( (voltage, tri_stim, spectrum) )
        return vol_col_spec_list


    def calibrate(self, imi=0.5, n=50, each=1):
        """
        Calibrate calibrates tubes with EyeOne Pro. EyeOne Pro should be
        connected to the computer. The calibration takes around 2 ?? minutes.

        :Paramter:

            imi : *0.5* or any positive float
                inter measurement interval in seconds
            n : *50* or any positive integer greater 2
                number of steps per tube to calibrate (must be greater
                equal 2)
            each : *1* or any positive integer
                number of measurements per color

        """
        # TODO generate logfile for every calibration
        # TODO check what happens, if fitting of the curves failed!
        #      it should give a reasonable error message and stores the
        #      data in a way, that it is easy to refit.
        self.printNote()

        if not self.eyeone.is_calibrated:
            self.eyeone.calibrate()

        # Measurement
        self.setVoltages( (0xFFF, 0xFFF, 0xFFF) )
        print("\nPlease put EyeOne Pro in measurement position and "
        + "press key to start measurement.")
        print("\nTurn off blue and green tubes!"
        + "\nPress key to start measurement of RED tubes.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")
        measure_red = self.measureOneColorChannel(imi=imi, color="red",
                n=n, each=each)
        voltages_r = measure_red[0]
        xyY_r = measure_red[1]
        spectra_r = measure_red[2]

        self.setVoltages( (0xFFF, 0xFFF, 0xFFF) )
        print("\nTurn off red and blue tubes!"
        + "\nPress key to start measurement of GREEN tubes.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")
        measure_green = self.measureOneColorChannel(imi=imi, color="green",
                n=n, each=each)
        voltages_g = measure_green[0]
        xyY_g = measure_green[1]
        spectra_g = measure_green[2]

        self.setVoltages( (0xFFF, 0xFFF, 0xFFF) )
        print("\nTurn off red and green tubes!"
        + "\nPress key to start measurement of BLUE tubes.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")
        measure_blue = self.measureOneColorChannel(imi=imi, color="blue",
                n=n, each=each)
        voltages_b = measure_blue[0]
        xyY_b = measure_blue[1]
        spectra_b = measure_blue[2]
        
        self.setVoltages( (0xFFF, 0xFFF, 0xFFF) )
        print("\nTurn ON red, green and blue tubes!"
        + "\nPress key to start measurement of ALL tubes.")
        while(self.eyeone.I1_KeyPressed() != eNoError):
            time.sleep(0.01)
        print("Starting measurement...")
        measure_all = self.measureOneColorChannel(imi=imi, color="all",
                n=n, each=each)
        voltages_all = measure_all[0]
        xyY_all = measure_all[1]
        spectra_all = measure_all[2]
        
        print("Measurement finished.")
        self.setVoltages( (0x0, 0x0, 0x0) ) # to signal that the
                                            # measurement is over

        # write data to hard drive
        # TODO output.py
        with open('calibdata/measurements/calibration_tubes_raw_' +
                time.strftime("%Y%m%d_%H%M") +  '.txt', 'w') as calibFile:
            calibFile.write("voltage, xyY, spectra\n") # TODO not just with 3 values but with 3 + 3 + 36
            for voltages in (voltages_r, voltages_g, voltages_b):
                for i in range(len(voltages)):
                    calibFile.write(", ".join([str(x) for x in voltages[i]]) +
                                    ", " + ", ".join([str(x) for x in
                                        xyY_list[i]]) +
                                    ", " + ", ".join([str(x) for x in
                                        spectra[i]]) + 
                                    "\n")

        with open('calibdata/measurements/calibration_tubes_raw_' +
                time.strftime("%Y%m%d_%H%M") +  '.pkl', 'w') as f:
            pickle.dump(voltage_r, f)
            pickle.dump(voltage_g, f)
            pickle.dump(voltage_b, f)
            pickle.dump(xyY_r, f)
            pickle.dump(xyY_g, f)
            pickle.dump(xyY_b, f)

        try:
            # fit a luminance function -- non-linear regression model based
            # on Pinheiro & Bates (2000)

            def func(x, a, b, c):
                return a + (b - a)*exp(-exp(c)*x)

            # red channel
            Y_r = [x[2] for x in xyY_r]
            v_r = [x[2] for x in voltages_r]
            popt_r, pcov_r = curve_fit(func, v_r, Y_r, p0=[50, -10, -7])
            
            # green channel
            Y_g = [x[2] for x in xyY_g]
            v_g = [x[2] for x in voltages_g]
            popt_g, pcov_g = curve_fit(func, v_g, Y_g, p0=[50, -10, -7])

            # blue channel
            Y_b = [x[2] for x in xyY_b]
            v_b = [x[2] for x in voltages_b]
            popt_b, pcov_b = curve_fit(func, v_b, Y_b, p0=[50, -15, -10])

            print("Parameters estimated.")
        except:
            print("FAILED to estimate parameters of tubes.\n" +
                  "Look at calibration_tubes_raw_XX.txt for the data.")
            return

        # save all created objects to calibration_tubes.txt
        with open('calibdata/measurements/calibration_tubes_tubes' +
                time.strftime("%Y%m%d_%H%M") +  '.txt', 'w') as calibFile:
            calibFile.write('voltages R:' + str(v_r) + '\n')
            calibFile.write('voltages G:' + str(v_g) + '\n')
            calibFile.write('voltages B:' + str(v_b) + '\n')
            calibFile.write('Y R:' + str(Y_r) + '\n')
            calibFile.write('Y G:' + str(Y_g) + '\n')
            calibFile.write('Y B:' + str(Y_b) + '\n')
            calibFile.write('parameters R:' + str(popt_r) + '\n')
            calibFile.write('parameters G:' + str(popt_g) + '\n')
            calibFile.write('parameters B:' + str(popt_b) + '\n')

        # save the estimated parameters to CalibTubes object
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
        self.is_calibrated = True
        print("Calibration of tubes finished.")

    def measureOneColorChannel(self, color, imi=0.5, n=50, each=1):
        """
        Measures one color tubes from low to high luminosity.

            * color -- string one of "red", "green", "blue", "all"
            * imi -- inter measurement interval in seconds
            * n -- number of steps >= 2
            * each -- number of measurements per color

        Returns triple of lists (voltages, rgb, spectra).
        
        This function immediately starts measuring. There is no prompt to
        start measurement.

        """
        if not self.eyeone.is_calibrated:
            self.eyeone.calibrate()
        
        # define some variables
        # generating the tested voltages (r, g, b)
        voltages = list()

        step = int((0xFFF-0x400)/float(n-1))

        if color == "red":
            for i in range(n):
                for j in range(each):
                    voltages.append( ((0x400 + step * i), 0xFFF, 0xFFF) )
        elif color == "green":
            for i in range(n):
                for j in range(each):
                    voltages.append( (0xFFF, (0x400 + step * i), 0xFFF) )
        elif color == "blue":
            for i in range(n):
                for j in range(each):
                    voltages.append( (0xFFF, 0xFFF, (0x400 + step * i)) )
        elif color == "all":
            for i in range(n):
                for j in range(each):
                    voltages.append( ((0x400 + step * i), (0x400 + step * i), (0x400 + step * i)) )
        else:
            raise ValueError("color in measureOneColorChannel must be one"
            + "of 'red', 'green', 'blue' and not %s" %str(color))

        tri_stim = (c_float * TRISTIMULUS_SIZE)() # memory where EyeOne Pro
                                                  # saves tristim.
        spectrum = (c_float * SPECTRUM_SIZE)()    # memory where EyeOne Pro
                                                  # saves spectrum.
        rgb_list = list()
        spectra_list = list()

        for voltage in voltages:
            self.setVoltages(voltage)
            print(voltage)
            time.sleep(imi) # to give the EyeOne Pro time to adapt and to
                            # reduce carry-over effects
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for voltage %s ." %str(voltage))
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tristim for voltage %s ."
                        %str(voltage))
            rgb_list.append(list(tri_stim))
            if(self.eyeone.I1_GetSpectrum(spectrum, 0) != eNoError):
                print("Failed to get spectrum for voltage %s ."
                        %str(voltage))
            spectra_list.append(list(spectrum))

        return (voltages, rgb_list, spectra_list)

    def saveParameter(self, filename="./lastParameterTubes.pkl"):
        """
        Saves parameters used for interpolation function.
        """
        # TODO warn if a file gets replaced?
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
        # TODO what to do, if file doesn't exist? Throw exception?
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
        self.is_calibrated = True


    def plotCalibration(self):
        """
        plotCalibration plots luminance curves for each channel (data and
        fitted curve).
        """
        # TODO implement with matplotlib --> till then use
        # plotCalibration.R in achrolabutils
        pass

    def guessVoltages(self, Y):
        """
        Guesses voltages from parameters from calibration as a crude
        starting value and returns triple of integers.

        Y is target luminance of monitor. The individual color for each
        channel is taken from an old calibration that looked good and
        assumes that the ratio of red, green, and blue is constant for
        different intensities. This is of course very crude!
        """

        Y_r = 6.173447/(6.173447+22.92364+4.036948)*Y
        Y_g = 22.92364/(6.173447+22.92364+4.036948)*Y
        Y_b = 4.036948/(6.173447+22.92364+4.036948)*Y
        
        def inv(y, a, b, c):
            return -log((y - a)/(b - a))/exp(c)

        vol_r = inv(Y_r, self.red_p1, self.red_p2, self.red_p3)
        vol_g = inv(Y_g, self.green_p1, self.green_p2, self.green_p3)
        vol_b = inv(Y_b, self.blue_p1, self.blue_p2, self.blue_p3)
        
        voltages = ( int(vol_r), int(vol_g), int(vol_b) )

        return voltages

