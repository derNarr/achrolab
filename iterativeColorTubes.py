#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ./achrolabutils/iterativColorTubes.py
#
# (c) 2010-2011 Konstantin Sering <konstantin.sering [aet] gmail.com>
#     and Dominik Wabersich <wabersich [aet] gmx.net>
# GPL 3.0+ or (cc) by-sa (http://creativecommons.org/licenses/by-sa/3.0/)
#
# last mod 2011-05-03, KS

from colormath.color_objects import xyYColor,RGBColor,SpectralColor
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
            f.write(str(xyY.xyy_x) + ", " + str(xyY.xyy_y) + ", " +
                    str(xyY.xyy_Y) + "\n")
        f.close()
     


    ##########################################################################
    ###  Use xyY colors  #####################################################
    ##########################################################################

    # returns tuple
    def xyYdiff(self, color1, color2):
        if isinstance(color1, xyYColor):
            (x1, y1, z1) = (color1.xyy_x, color1.xyy_y, color1.xyy_Y)
        else:
            (x1, y1, z1) = (color1[0], color1[1], color1[2])
        if isinstance(color2, xyYColor):
            (x2, y2, z2) = (color2.xyy_x, color2.xyy_y, color2.xyy_Y)
        else:
            (x2, y2, z2) = (color2[0], color2[1], color2[2])
        return (x2 - x1, y2 - y1, z2 - z1)

    # returns float
    def xyYnorm(self, color):
        if isinstance(color, tuple):
            xyY = xyYColor(color[0], color[1], color[2])
        else:
            xyY = color
        x = 1 * xyY.xyy_x
        y = 1 * xyY.xyy_y
        z = 10**-2 * xyY.xyy_Y
        return (x**2 + y**2 + z**2)**0.5

    # returns float
    def norm(self, vec):
        return (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5

    # returns xyYColor
    def xyYnew_color(self, old_color, vec):
        return xyYColor(old_color.xyy_x + vec[0],
                        old_color.xyy_y + vec[1],
                        old_color.xyy_Y + vec[2])


    # returns tuple (voltages, tri_stim)  (last inputColor)
    def iterativeColormatch(self, targetColor, epsilon=0.01,
        streckung=1.0, imi=0.5, max_iterations=50):
        """
        iterativeColormatch tries to match the measurement of the tubes to the
        targetColor.
        * targetColor -- colormath color object
        * epsilon
        * streckung
        * imi -- intermeasurement intervall
        * max_iterations
        """
        # set colors
        if isinstance(targetColor, tuple):
            targetColor = xyYColor(targetColor[0], targetColor[1],
                    targetColor[2])
        else:
            targetColor = targetColor.convert_to('xyY')
        inputColor = targetColor
        measuredColor = xyYColor(0,0,0)
        diffColor = (1.0, 1.0, 1.0)
        
        self.tubes.setColor(inputColor)
        
        print("Start measurement...")
        
        tri_stim = (c_float * TRISTIMULUS_SIZE)()
        i=0
        print("\n\nTarget: " + str(targetColor) + "\n")
        
        while ((norm(diffColor) > epsilon)):
            if i == max_iterations:
                inputColor = None
                print("not converged")
                return (None, None)
            self.tubes.setColor(inputColor)
            i = i + 1 # new round
            time.sleep(imi)
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for color %s ." %str(inputColor))
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus for color %s ."
                        %str(inputColor))
            measuredColor = xyYColor(tri_stim[0], tri_stim[1], tri_stim[2])
            print(str(measuredColor))
            # correct the new color to a probably reduced (streckung < 1)
            # negative difference to the measured color.
            diffColor = [x*streckung for x in xyYdiff(measuredColor, targetColor)]
            print("diff: " + str(diffColor))
            inputColor = xyYnew_color(inputColor, diffColor)
                
        
        print("\nFinal inputColor: " + str(inputColor) + "\n\n")
        rgb = inputColor.convert_to('rgb', target_rgb='sRGB', clip=False)
        voltages = (self.tubes._sRGBtoU_r(rgb.rgb_r), 
                    self.tubes._sRGBtoU_g(rgb.rgb_g),
                    self.tubes._sRGBtoU_b(rgb.rgb_b))
        return (voltages, measuredColor)


    ###########################################################################
    ### TUNING ################################################################
    ###########################################################################

    # returns xyYColor
    def newVoltages(self, old_voltages, vec):
        return [int(x) for x in (old_voltages[0] + vec[0],
                                 old_voltages[1] + vec[1],
                                 old_voltages[2] + vec[2])]



    # return tuple of (voltages, color)
    def measureColor(self, voltages, imi=0.5):
        """
        measureColor measures inputColor and sleeps imi-time. Returns measured Color.
        * inputColor
        * imi-- intermeasurement intervall
        """
        tri_stim = (c_float * TRISTIMULUS_SIZE)()
        self.tubes.setVoltage(voltages)
        time.sleep(imi)
        # TODO average multiple measurement
        if(self.eyeone.I1_TriggerMeasurement() != eNoError):
            print("Measurement failed for color %s ." %str(inputColor))
        if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
            print("Failed to get tri stimulus for color %s ."
                    %str(inputColor))
        measuredColor = xyYColor(tri_stim[0], tri_stim[1], tri_stim[2])
        return (voltages, measuredColor)


    def createMeasurementSeries(self, starting_voltages, step_R=0,
            step_G=0, step_B=0, series_quantity=10, imi=0.5):
        """
        createMeasurementSeries creates and returns a list of measured Points
        (voltages, xyYColor).
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
        input_voltages = newVoltages(starting_voltages, diff_voltages)
        i = 0
        diff_voltages = (step_R,step_G,step_B)
        measured_series = []
        while (i < series_quantity):
            i = i + 1 # new round
            measured_voltage_color = measureColor(input_voltages,
                    self.tubes, self.eyeone, imi=imi)
            measured_series.append( measured_voltage_color )
            print(str(measured_voltage_color[1]))
            print("diff: " + str(diff_voltages))
            input_voltages = newVoltages(input_voltages, diff_voltages)
        return measured_series


    def findBestColor(self, measured_color_red, measured_color_green,
            measured_color_blue, target_color):
        """
        findBestColor returns a color, which is nearest targetColor.
        * measured_color -- contains the measured colors for each channel
        * target_color
        """
        voltage_color_list = []
        voltage_color_list.extend( measured_color_red )
        voltage_color_list.extend( measured_color_green )
        voltage_color_list.extend( measured_color_blue )
        return min(voltage_color_list, key=(lambda a: xyYnorm(xyYdiff(a[1],
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
            measured_series.append( measureColor(voltages, self.tubes,
                self.eyeone) )

        return measured_series


    # returns tuple (voltages, tri_stim)  (last inputColor)
    def iterativeColormatch2(self, targetColor, start_voltages=None,
            iterations=50, stepsize=10, imi=0.5):
        """
        iterativeColormatch2 tries to match the measurement of the tubes to the
        targetColor (with a different method than iterativeColormatch).
        * targetColor -- colormath color object or tuple of (x, y, Y)
        * iterations
        """
        # TODO: extra iterations for the measurement points
        # set colors
        # TODO: imi
        if isinstance(targetColor, tuple):
            targetColor = xyYColor(targetColor[0], targetColor[1],
                    targetColor[2])

        rgb = targetColor.convert_to('rgb', target_rgb='sRGB', clip=False)
        if start_voltages:
            input_voltages = start_voltages
        else:
            input_voltages = (self.tubes._sRGBtoU_r(rgb.rgb_r), 
                         self.tubes._sRGBtoU_g(rgb.rgb_g),
                         self.tubes._sRGBtoU_b(rgb.rgb_b))
        measuredColor = xyYColor(0,0,0)
        diffColor = (1.0, 1.0, 1.0)
        
        print("Start measurement...")
        
        i=0
        print("\n\nTarget: " + str(targetColor) + "\n")

        while (i < iterations):
            i = i + 1

            # create (voltages, color) list
            measuredColorList_R = createMeasurementSeries(input_voltages,
                    self.tubes, self.eyeone, step_R=stepsize, series_quantity=20)
            measuredColorList_G = createMeasurementSeries(input_voltages,
                    self.tubes, self.eyeone, step_G=stepsize, series_quantity=20)
            measuredColorList_B = createMeasurementSeries(input_voltages,
                    self.tubes, self.eyeone, step_B=stepsize, series_quantity=20)

            # save data for debugging
            filename = ("tune_r" + str(int(rgb.rgb_r)) + "g" +
                    str(int(rgb.rgb_g)) + "b" +
                    str(int(rgb.rgb_b)) + "_iteration" + str(i))
            write_data(measuredColorList_R, filename + "_chR.csv")
            write_data(measuredColorList_G, filename + "_chG.csv")
            write_data(measuredColorList_B, filename + "_chB.csv")

            # measure in the surrounding of the nearest points 
            measuredColor_R = measureAtColor(
                    findBestColor(measuredColorList_R), self.tubes,
                    self.eyeone, channel="red", span=stepsize)
            measuredColor_G = measureAtColor(
                    findBestColor(measuredColorList_G), self.tubes,
                    self.eyeone, channel="green", span=stepsize)
            measuredColor_B = measureAtColor(
                    findBestColor(measuredColorList_B), self.tubes,
                    self.eyeone, channel="blue", span=stepsize)

            # now serch for point with the smallest distance to targetColor
            # should return inputColor or inputVoltages
            best_voltage_color = findBestColor(measuredColor_R,
                    measuredColor_G, measuredColor_B, targetColor)
            input_voltages = best_voltage_color[0]
        
        print("\nFinal voltages:" + str(best_voltage_color[0]) + "\n\n")
        return best_voltage_color


    ##########################################################################
    ###  Use RGB colors  #####################################################
    ##########################################################################

    # returns tuble
    def RGBdiff(self, color1, color2):
        return (color2.rgb_r - color1.rgb_r,
                color2.rgb_g - color1.rgb_g,
                color2.rgb_b - color1.rgb_b)

    # returns float 
    def RGBnorm(self, color):
        return (color.rgb_r**2 + color.rgb_g**2 + color.rgb_b**2)**0.5

    # returns float
    def norm(self, vec):
        return (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5

    # returns Color
    def RGBnew_color(self, old_color, vec):
        return RGBColor(old_color.rgb_r + vec[0],
                        old_color.rgb_g + vec[1],
                        old_color.rgb_b + vec[2])


    # returns tuple (voltages, tri_stim)  (last inputColor)
    def iterativeColormatchRGB(self, targetColor, epsilon=5.0,
        streckung=1.0, imi=0.5, max_iterations=50):
        """
        iterativeColormatch tries to match the measurement of the tubes to the
        targetColor.
        * targetColor -- colormath color object
        * epsilon
        * streckung
        * imi -- intermeasurement intervall
        * max_iterations
        """
        # set colors
        if isinstance(targetColor, tuple):
            targetColor = RGBColor(targetColor[0], targetColor[1],
                    targetColor[2])
        else:
            targetColor = targetColor.convert_to('rgb', target_rgb='sRGB',
                    clip=False)
        inputColor = targetColor
        measuredColor = RGBColor(0,0,0)
        diffColor = (100.0, 100.0, 100.0)
        
        self.tubes.setColor(inputColor)
        
        print("Start measurement...")
        
        tri_stim = (c_float * TRISTIMULUS_SIZE)()
        i=0
        print("\n\nTarget: " + str(targetColor) + "\n")
        
        while ((norm(diffColor) > epsilon)):
            if i == max_iterations:
                inputColor = None
                print("not converged")
                return (None, None)
            i = i + 1 # new round
            self.tubes.setColor(inputColor)
            print("set tubes to: " + str( (self.tubes._sRGBtoU_r(inputColor.rgb_r), 
                    self.tubes._sRGBtoU_g(inputColor.rgb_g),
                    self.tubes._sRGBtoU_b(inputColor.rgb_b)) ) )
            time.sleep(imi)
            if(self.eyeone.I1_TriggerMeasurement() != eNoError):
                print("Measurement failed for color %s ." %str(inputColor))
            if(self.eyeone.I1_GetTriStimulus(tri_stim, 0) != eNoError):
                print("Failed to get tri stimulus for color %s ."
                        %str(inputColor))
            xyY = xyYColor(tri_stim[0], tri_stim[1], tri_stim[2])
            measuredColor = xyY.convert_to('rgb', target_rgb='sRGB', clip=False)
            print("target color: " + str(targetColor))
            print("measured color: " + str(measuredColor))
            # correct the new color to a probably reduced (streckung < 1)
            # negative difference to the measured color.
            diffColor = [x*streckung for x in RGBdiff(measuredColor, targetColor)]
            print("diff: " + str(diffColor) + "\n")
            inputColor = RGBnew_color(inputColor, diffColor)
                
        
        print("\nFinal inputColor: " + str(inputColor) + "\n\n")
        #rgb = inputColor.convert_to('rgb', target_rgb='sRGB', clip=False)
        voltages = (self.tubes._sRGBtoU_r(inputColor.rgb_r), 
                    self.tubes._sRGBtoU_g(inputColor.rgb_g),
                    self.tubes._sRGBtoU_b(inputColor.rgb_b))
        return (voltages, measuredColor)

