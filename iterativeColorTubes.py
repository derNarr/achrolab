#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./achrolabutils/iterativColorTubes.py
#
# (c) 2010-2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
#     and Dominik Wabersich <wabersich [aet] gmx.net>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-06-28, KS

from devtubes import Tubes
from eyeone.EyeOne import EyeOne
from eyeone.EyeOneConstants import  (I1_MEASUREMENT_MODE, 
                                    I1_SINGLE_EMISSION,
                                    eNoError,
                                    COLOR_SPACE_KEY, 
                                    COLOR_SPACE_CIExyY,
                                    TRISTIMULUS_SIZE)
from ctypes import c_float
import time
from exceptions import ValueError
from psychopy import visual
import rpy2.robjects as robjects
# want to run R-commands with R("command")
R = robjects.r

class IterativeColorTubes(object):

    def __init__(self, tubes=Tubes, eyeone=EyeOne):
       """
       * self -- IterativeColorTubes object
       * tubes -- achrolab.devtubes.Tubes object
       * eyeone -- calibrated EyeOne object
       """
       self.tubes = tubes
       self.eyeone = eyeone

    def write_data(self, voltage_color_list, filename):
        f = open("./tune/" + filename, "w")
        f.write("voltage_r, voltage_g, voltage_b, xyY_x, xyY_y, xyY_Y\n") 
        for vc in voltage_color_list:
            for voltage in vc[0]:
                f.write(str(voltage) + ", ")
            xyY = vc[1]
            f.write(str(xyY[0]) + ", " + str(xyY[1]) + ", " +
                    str(xyY[2]) + "\n")
        f.close()
     


    ##########################################################################
    ###  Use xyY colors  #####################################################
    ##########################################################################

    # returns tuple
    def xyYdiff(self, color1, color2):
        """
        Simply calculates the difference between every element of the two
        colors. There are many different ways to do it and this is not the
        fanciest one.
        """
        return (color2[0] - color1[0],
                color2[1] - color1[1],
                color2[2] - color1[2])

    # returns float
    def xyYnorm(self, xyY):
        """
        Calculates an abitrary norm for a given xyY color (as a tuple).

        Here is the right place to tweak a bit. This norm will be used to
        minimize the distance between two matching colors.
        """
        x = 1 * xyY[0] #x
        y = 1 * xyY[1] #y
        z = 10**-2 * xyY[2] #Y
        return (x**2 + y**2 + z**2)**0.5

    # returns float
    def norm(self, vec):
        """
        Calculates the euclidean norm of a given vector (as a tuple).
        """
        return (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5

    # returns tuple
    def xyYNewColor(self, old_color, vec):
        """
        Adds the components of the vector (as a tuple) to the components of
        the xyY color (as a tuple).
        """
        return (old_color[0] + vec[0],
                old_color[1] + vec[1],
                old_color[2] + vec[2])


    # returns tuple (voltages, tri_stim)  (last input_color)
    def iterativeColorMatch(self, target_color, epsilon=0.01,
        dilation=1.0, imi=0.5, max_iterations=50):
        """
        iterativeColorMatch tries to match the measurement of the tubes to the
        target_color.
        * target_color -- tuple containing the xyY values as floats
        * epsilon
        * dilation
        * imi -- intermeasurement intervall
        * max_iterations
        """
        # set colors
        input_color = target_color
        measured_color = (0,0,0)
        diff_color = (1.0, 1.0, 1.0)
        
        self.tubes._tub.setColor(input_color)
        
        print("Start measurement...")
        
        tri_stim = (c_float * TRISTIMULUS_SIZE)()
        i=0
        print("\n\nTarget: " + str(target_color) + "\n")
        
        while ((self.norm(diff_color) > epsilon)):
            if i == max_iterations:
                input_color = None
                print("not converged")
                return (None, None)
            self.tubes._tub.setColor(input_color)
            i = i + 1 # new round
            time.sleep(imi)
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for color %s ." %str(input_color))
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus for color %s ."
                        %str(input_color))
            measured_color = (tri_stim[0], tri_stim[1], tri_stim[2])
            print(str(measured_color))
            # correct the new color to a probably reduced (dilation < 1)
            # negative difference to the measured color.
            diff_color = [x*dilation for x in self.xyYdiff(measured_color, target_color)]
            print("diff: " + str(diff_color))
            input_color = self.xyYNewColor(input_color, diff_color)
                
        
        print("\nFinal input_color: " + str(input_color) + "\n\n")
        voltages = self.tubes.xyYtoU(input_color)
        return (voltages, measured_color)


    ###########################################################################
    ### TUNING ################################################################
    ###########################################################################

    # returns (x, y, Y)
    def newVoltages(self, old_voltages, vec):
        return [int(x) for x in (old_voltages[0] + vec[0],
                                 old_voltages[1] + vec[1],
                                 old_voltages[2] + vec[2])]



    # return tuple of (voltages, (x, y, Y) )
    def measureColor(self, voltages, imi=0.5):
        """
        measureColor measures color for given voltages and sleeps imi-time.
        Returns measured Color.

        * voltages -- tuple
        * imi -- intermeasurement intervall
        """
        tri_stim = (c_float * TRISTIMULUS_SIZE)()
        self.tubes.setVoltages(voltages)
        time.sleep(imi)
        # TODO average multiple measurement
        if(self.eyeone.I1_TriggerMeasurement() != eNoError):
            print("Measurement failed for color %s ." %str(input_color))
        if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
            print("Failed to get tri stimulus for color %s ."
                    %str(input_color))
        measured_color = (tri_stim[0], tri_stim[1], tri_stim[2])
        return (voltages, measured_color)


    def createMeasurementSeries(self, starting_voltages, step_R=0,
            step_G=0, step_B=0, series_quantity=10, imi=0.5):
        """
        createMeasurementSeries creates and returns a list of measured Points
        (voltages, (x,y,Y) ).
        * starting_voltages
        * step_R -- red value step between two points
        * step_G -- green value step between two points
        * step_B -- blue value step between two points
        * series_quantity -- number of measurements
        * imi -- sleep time between two measurements
        """
        diff_voltages = (-0.5*series_quantity*step_R,
                     -0.5*series_quantity*step_G,
                     -0.5*series_quantity*step_B)
        input_voltages = self.newVoltages(starting_voltages, diff_voltages)
        i = 0
        diff_voltages = (step_R,step_G,step_B)
        measured_series = []
        while (i < series_quantity):
            i = i + 1 # new round
            measured_voltage_color = self.measureColor(input_voltages,
                    imi=imi)
            measured_series.append( measured_voltage_color )
            print(str(measured_voltage_color[1]))
            print("diff: " + str(diff_voltages))
            input_voltages = self.newVoltages(input_voltages, diff_voltages)
        return measured_series


    def findBestColor(self, voltage_color_list, target_color):
        """
        findBestColor returns a color, which is nearest target_color.
        * voltage_color_list -- list containing the measured colors
            voltages tuple 
        * target_color
        """
        return min(voltage_color_list, key=(lambda a: self.xyYnorm(self.xyYdiff(a[1],
            target_color))))

    def measureAtColor(self, voltages_color, channel, span, stepsize=1):
        """
        measureAtColor returns a list of measured Colors wich are half of range
        size up and down the channel.
        * voltages_color
        * span -- number of points
        * stepsize -- integer
        """
        if channel=="red":
            index = 0
        elif channel=="green":
            index = 1
        elif channel=="blue":
            index = 2
        else:
            raise ValueError("channel must be one of 'red', 'green' or 'blue'")
        
        voltages = list(voltages_color[0]) 
        measured_series = []

        voltages[index] = int(voltages[index] - 0.5 * span * stepsize)

        for i in range(span+1):
            voltages[index] = int(voltages[index] + i * stepsize)
            print("between points voltages: " + str(voltages))
            measured_series.append( self.measureColor(voltages) )

        return measured_series


    # returns tuple (voltages, tri_stim)  (last input_color)
    def iterativeColorMatch2(self, target_color, start_voltages=None,
            iterations=50, stepsize=10, imi=0.5):
        """
        iterativeColorMatch2 tries to match the measurement of the tubes to the
        target_color (with a different method than iterativeColorMatch).
        * target_color -- tuple of (x, y, Y)
        * iterations
        """
        # TODO: extra iterations for the measurement points
        # set colors
        # TODO: imi
        if start_voltages:
            input_voltages = start_voltages
        else:
            input_voltages = self.tubes.xyYtoU(target_color)
        print("Start measurement...")
        i=0
        print("\n\nTarget (x,y,Y): " + str(target_color) + "\n")

        while (i < iterations):
            i = i + 1

            # create (voltages, color) list
            measured_color_list_R = self.createMeasurementSeries(input_voltages,
                    step_R=stepsize, series_quantity=20)
            measured_color_list_G = self.createMeasurementSeries(input_voltages,
                    step_G=stepsize, series_quantity=20)
            measured_color_list_B = self.createMeasurementSeries(input_voltages,
                    step_B=stepsize, series_quantity=20)

            # save data for debugging
            filename = ("tune_x" + str(target_color[0]) + "y" +
                    str(target_color[1]) + "Y" +
                    str(target_color[2]) + "_iteration" + str(i))
            self.write_data(measured_color_list_R, filename + "_chR.csv")
            self.write_data(measured_color_list_G, filename + "_chG.csv")
            self.write_data(measured_color_list_B, filename + "_chB.csv")

            # measure in the surrounding of the nearest points 
            measured_color_R = self.measureAtColor(
                    self.findBestColor(measured_color_list_R, target_color), 
                    channel="red", span=stepsize)
            measured_color_G = self.measureAtColor(
                    self.findBestColor(measured_color_list_G, target_color), 
                    channel="green", span=stepsize)
            measured_color_B = self.measureAtColor(
                    self.findBestColor(measured_color_list_B, target_color), 
                    channel="blue", span=stepsize)

            # now serch for point with the smallest distance to target_color
            # should return input_color or input_voltages
            measured_voltage_color_list = []
            measured_voltage_color_list.extend( measured_color_R )
            measured_voltage_color_list.extend( measured_color_G )
            measured_voltage_color_list.extend( measured_color_B )
            best_voltage_color = self.findBestColor(
                    measured_voltage_color_list, target_color)
            input_voltages = best_voltage_color[0]
        
        print("\nFinal voltages:" + str(best_voltage_color[0]) + "\n\n")
        return best_voltage_color



